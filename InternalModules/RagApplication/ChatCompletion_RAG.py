import json
import InternalModules.OpenAiEnvironment.AzureAiClient as AzureAiClient
import InternalModules.RagApplication.RagApplication as RagApplication

## Create embeddings from the user input, combine it with the nearest neighbors of the database, and 
##   use it to add context to the prompt, then perform the chatbot completion
def GetContextUsingInputAndCompleteChat(user_input, nearest_neighbors_estimator, context_embeddings_dataframe):
    response = None
    emsgContext = f'in ChatCompletion_RAG.py.GetContextUsingInputAndCompleteChat(...)'
    emsgOperation = f''
    try:
        system_content = f"You are an AI assiatant that helps with AI questions."
        if user_input:
            # Convert the question to a query vector
            query_vector = AzureAiClient.CreateEmbeddings(user_input)
            if query_vector and nearest_neighbors_estimator and (context_embeddings_dataframe is not None):
                # Find the most similar documents
                #   'indices' - there is an item that is the index in 'chunks' (also 'embeddings') of the nearest neighbor of each embedding
                #       that is represented in the nearest_neighbors_estimator and context_embeddings_dataframe['chunks'] (also ['embeddings'])
                #   'distances' - there is an item for each chunk (also embedding) with the distance
                #           from the embedding indicated by the corresponding index in 'indices'
                distances, indices = nearest_neighbors_estimator.kneighbors([query_vector])
                # add documents to query to provide context
                if (indices is not None) and (len(indices) > 0):
                    system_content += f"; Additional Information - "
                    for index in indices[0]:
                        chunk = context_embeddings_dataframe['chunks'].iloc[index]
                        """ print(f"context_embeddings_dataframe['chunks'].iloc[" + str(index) + "] = " + chunk)
                        print(f" ") """
                        system_content += chunk
            else:
                user_input = "No user input."
            
            # create a message object
            messages=[
                {"role": "system", "content": system_content},
                {"role": "user", "content": user_input}
            ]
            print(f"messages = " + json.dumps(messages))
            response = AzureAiClient.GetClientAndCompleteChat(messages, 0.7, withRawResponse = True)
            #
            return response 
        else:
            raise NameError(f'user_input is None.')        

    except NameError as e:
        emsg = (f'NameError Exception ' + emsgOperation + ' ' + emsgContext + f': ' + repr(e))
        raise Exception(emsg)

    except Exception as e:
        emsg = (f'Exception ' + emsgOperation + f' ' + emsgContext + f': ' + repr(e))
        raise Exception(emsg)
        

def CreateContextAndUseInputThenCompleteChat(user_input):
    response_chat = None
    emsgContext = f'in ChatCompletion_RAG.py.CreateContextAndUseInputThenCompleteChat(...)'
    emsgOperation = f''
    try:
        emsgOperation = f'validating user_input'
        if user_input:
            ## Convert the files to embeddings, etc
            emsgOperation = f'converting Data files to embeddings'
            values = RagApplication.convertDataFilesToEmbeddings()
            if values and (len(values) > 1):
                """ flattened_df = values[1]
                print(f"flattened_df['chunks'] = ")
                print(flattened_df['chunks']) """
                ## Use RAG method of generating a response
                emsgOperation = f'getting the context and completing the chat with values from Data files'
                response_chat = GetContextUsingInputAndCompleteChat(user_input, values[0], values[1])
            else:
                emsgOperation = f'getting the context and completing the chat when no values were returned from Data files'
                response_chat = GetContextUsingInputAndCompleteChat(user_input, None, None) 
            if response_chat:
                return response_chat
            else:
                raise NameError(f'response_chat is None.')
        else:
            raise NameError(f'user_input is None.')  

    except NameError as e:
        emsg = (f'NameError Exception ' + emsgOperation + ' ' + emsgContext + f': ' + repr(e))
        raise Exception(emsg)
    except Exception as e:
        emsg = (f'Exception ' + emsgOperation + f' ' + emsgContext + f': ' + repr(e))
        raise Exception(emsg)
        