import pandas as pd
from sklearn.neighbors import NearestNeighbors

import InternalModules.OpenAiEnvironment.AzureAiClient as AzureAiClient
import InternalModules.OpenAiEnvironment.AzureAiFileManagement as AzureAiFileManagement
import InternalModules.OpenAiEnvironment.AzureAiEmbeddings as AzureAiEmbeddings
import InternalModules.FileManagement.FileManagement as FileManagement

def convertDataFilesToEmbeddings():
    emsgContext = f"RagApplication.convertDataFilesToEmbeddings()"
    emsgOperation = f""
    #
    values = None
    purpose_fine_tune = f"fine-tune"
    try:
        emsgOperation = f"retrieving the file contents from the data files"
        data_contents = RetrieveFileContents(purpose_fine_tune)
        if data_contents:
            emsgOperation = f"converting the file contents to embeddings"
            values = convertContentsToEmbeddings(data_contents)
            #
            return values
    except Exception as e:
        raise Exception( f"Exception in " + emsgContext + f" while " + emsgOperation + f": " + str({e}))

def RetrieveFileContents(purpose):
    file_contents = None
    client = AzureAiClient.GetClient()
    if client:
        file_ids = AzureAiFileManagement.GetFileIds(client, purpose)
        if file_ids:
            file_contents = AzureAiFileManagement.RetrieveFileContentsCombined(client, file_ids)
    return file_contents

"""
Return an array (values) with
    values[0] = A sklearn.neighbors.NearestNeighbors object; The fitted nearest neighbors estimator from the embeddings
    values[1] = A pandas.DataFrame object with
       'path' column - a row for each file with the path to the file
       'text' column - a row for each file with the text of the file
       'chunks' column - there is a row for each file x chunk combination
           each row contains a "word chunk" from the file that is 300 to 400 characters in length
       'embeddings' column - there is a row for each file x chunk combination
           each row contains the embedding created from the "word chunk" with the same index
       'indices' column - there is a row for the index in 'chunks' (also 'embeddings') of the nearest neighbor of each embedding
       'distances' column - there is a row for the distance to the nearest neighbor of each embedding
    
"""
def convertContentsToEmbeddings(data_contents):
    values = None
    
    ## Create a Knowledge Base as a pandas DataFrame  
    # Initialize an empty DataFrame
    df = pd.DataFrame(columns=['path', 'text'])

    # Fill Dataframe with the path and text of each file
    #print(f"data_contents: ")
    keys = data_contents.keys()
    for key in keys:
        content = data_contents.get(key)
        #print(f"content for key '" + key + f"': " + content)
        # Append the file path and text to the DataFrame
        df_new = pd.DataFrame([[key, content]], columns=['path', 'text'])
        df = pd.concat([df, df_new])
    df.head()
    #print(f" ")
    
    # Create a copy of the DataFrame and 
    #   add a 'chunks' column with the text of each file split into chunks of words 300 to 400 characters in length
    #       there is a row for each file
    #           each row has the 'path', 'text' and 'chunks' columns
    #               the 'chunks' column has an array of "words chunks" from the file that are 300 to 400 characters in length
    splitted_df = df.copy()
    splitted_df['chunks'] = splitted_df['text'].apply(lambda x: FileManagement.split_text_into_chunks_by_sentences(x))
    """ print(f"splitted_df.['chunks']: ")
    for split_df_chunk in splitted_df['chunks']:
        print(f"The current chunk: ")
        for index_in_chunk in range(len(split_df_chunk)):
            print(f"Item " + str(index_in_chunk) + f": " + split_df_chunk[index_in_chunk])
        print(f" ")
    print(f" ") """

    # Assuming 'chunks' is a column of lists in the DataFrame splitted_df, we will split the chunks into different rows
    #   In flattened_df, 
    #       'path' column - a row for each file with the path to the file
    #       'text' column - a row for each file with the text of the file
    #       'chunks' column - there is a row for each file x chunk combination
    #           each row contains a "word chunk" from the file that is 300 to 400 characters in length
    flattened_df = splitted_df.explode('chunks')

    flattened_df.head()

    # Add the chunks as embeddings to a collection of embeddings
    number_of_neighbors_to_find = 0
    embeddings = []
    #print(f"flattened_df['chunks']: ")
    for chunk in flattened_df['chunks']:
        number_of_neighbors_to_find = number_of_neighbors_to_find + 1
        #print(f"The current chunk: " + chunk)
        embeddings_local = AzureAiEmbeddings.CreateEmbeddings(chunk)
        embeddings.append(embeddings_local)
    #print(f" ")

    # Store the embeddings in the dataframe
    #   In flattened_df, 
    #       'path' column - a row for each file with the path to the file
    #       'text' column - a row for each file with the text of the file
    #       'chunks' column - there is a row for each file x chunk combination
    #           each row contains a "word chunk" from the file that is 300 to 400 characters in length
    #       'embeddings' column - there is a row for each file x chunk combination
    #           each row contains the embedding created from the "word chunk" with the same index
    flattened_df['embeddings'] = embeddings

    flattened_df.head()

    ## Retrieval - Vector search and similiarity between our prompt and the database
    # Creating an search index and reranking 

    embeddings = flattened_df['embeddings'].to_list()

    # Create the nearest neighbors estimator for the embeddings
    #   nbrs = The fitted nearest neighbors estimator from the embeddings
    nbrs = NearestNeighbors(n_neighbors=number_of_neighbors_to_find, algorithm='ball_tree').fit(embeddings)

    # To query the index, you can use the kneighbors method
    #   Returns the distances to and indices of the neighbors of each point.
    #       distances = Array representing the lengths to points
    #       indices = Indices of the nearest points in the population matrix.
    distances, indices = nbrs.kneighbors(embeddings)

    # Store the indices and distances in the DataFrame
    #   In flattened_df, 
    #       'path' column - a row for each file with the path to the file
    #       'text' column - a row for each file with the text of the file
    #       'chunks' column - there is a row for each file x chunk combination
    #           each row contains a "word chunk" from the file that is 300 to 400 characters in length
    #       'embeddings' column - there is a row for each file x chunk combination
    #           each row contains the embedding created from the "word chunk" with the same index
    #       'indices' column - there is a row for the index in 'chunks' (also 'embeddings') of the nearest neighbor of each embedding
    #       'distances' column - there is a row for each chunk (also embedding) with the distance
    #           from the embedding indicated by the corresponding index in 'indices'
    #           to the nearest neighbor of that item
    flattened_df['indices'] = indices.tolist()
    flattened_df['distances'] = distances.tolist()

    flattened_df.head()

    # Create return structure
    values = [nbrs, flattened_df]
    return values 