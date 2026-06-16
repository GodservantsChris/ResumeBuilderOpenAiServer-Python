import os
import openai.types.embedding as Embedding

import InternalModules.OpenAiEnvironment.AzureAiClient as AzureAiClient

def CreateEmbeddings(text) -> Embedding:
    embeddings = None
    emsgContext = f''
    emsgOperation = f''
    try:
        emsgOperation = f"getting the client object"
        client = AzureAiClient.GetClient()
        emsgOperation = f"getting the AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT environmental variable"
        deployment = os.getenv("AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT")
        emsgOperation = f"creating the embeddings"
        embeddings = client.embeddings.create(input = text, model=deployment).data[0].embedding
        if embeddings:
            return embeddings
        else:
            raise NameError
    except NameError as e:
        raise Exception(f'NameError Exception ' + emsgOperation + ' ' + emsgContext + f': ' + repr(e))
    except Exception as e:
        raise Exception(f'Exception ' + emsgOperation + f' ' + emsgContext + f': ' + repr(e) )

def CreateEmbedding(text, client, deployment) -> list[float]:
    embedding = None
    emsgContext = f'in AzureAiClient.CreateEmbeddings(text, client, deployment)'
    emsgOperation = f''
    try:
        emsgOperation = f"creating the embeddings"
        embeddings = client.embeddings.create(input = text, model=deployment)
        emsgOperation = f"validating the embeddings"
        if embeddings is not None:
            embedding = embeddings.data[0].embedding
            if embedding:
                return embedding
            else:
                raise NameError
        else: raise NameError
    except NameError as e:
        raise Exception(f'NameError Exception ' + emsgOperation + ' ' + emsgContext + f': ' + repr(e))
    except Exception as e:
        raise Exception(f'Exception ' + emsgOperation + f' ' + emsgContext + f': ' + repr(e) )
    
   
