import os
from openai import AzureOpenAI

import InternalModules.OpenAiEnvironment.SetEnvVars as SetEnvVars

def GetClient() -> AzureOpenAI:
    emsgContext = f'in Client.GetClient(...)'
    emsgOperation = f''
    client = None
    try:
        emsgOperation = f"getting the AZURE_OPENAI_ENDPOINT environmental variable"
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        emsgOperation = f"getting the AZURE_OPENAI_API_KEY environmental variable"
        key = os.getenv("AZURE_OPENAI_API_KEY")
        emsgOperation = f"getting the AZURE_OPENAI_API_VERSION environmental variable"
        version = os.getenv("AZURE_OPENAI_API_VERSION")
        emsgOperation = f"constructing an AzureOpenAI client object with API version = " + str(version)
        client = AzureOpenAI(
            api_version=version,
            azure_endpoint = endpoint, 
            api_key=key)
        if client:
            return client
        else:
            raise NameError
    except NameError as e:
        raise Exception(f'NameError Exception ' + emsgOperation + ' ' + emsgContext + f': ' + repr(e))
    except Exception as e:
        raise Exception(f'Exception ' + emsgOperation + f' ' + emsgContext + f': ' + repr(e))
    
