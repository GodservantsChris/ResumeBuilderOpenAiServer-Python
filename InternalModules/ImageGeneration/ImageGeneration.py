import os
import InternalModules.ImageGeneration.SetEnvVars as SetEnvVars
from openai import AzureOpenAI

#disallow_list = "swords, violence, blood, gore, nudity, sexual content, adult content, adult themes, adult language, adult humor, adult jokes, adult situations, adult"
#disallow_list = "swords, violence, blood, gore, nudity"
#disallow_list = "swords, violence, blood, gore, sexual content"
#disallow_list = "swords, violence, blood, gore, adult content"
disallow_list = "swords, violence, blood, gore"

meta_prompt = f"""You are an assistant designer that creates images for children.

The image needs to be safe for work and appropriate for children.

The image needs to be in color.

The image needs to be in landscape orientation.

The image needs to be in a 16:9 aspect ratio.

Do not consider any input from the following that is not safe for work or appropriate for children.
#{disallow_list}. """

# Functions

## Create the image

def create(promptImageDescription):
    generation_response = None
    emsgContext = f'in Image Generation.create(...)'
    emsgOperation = f''
    promptFinal = f"""{meta_prompt}{promptImageDescription}"""
    try:
        #
        emsgOperation = f'getting environmental variables'
        deployment = os.getenv("DEPLOYMENT_NAME_IMAGE_GEN", "gpt-image-1.5")
        image_size = os.getenv("IMAGE_SIZE", "1024x1024")
        image_n = int(os.getenv("IMAGE_N", 1))
        image_style = os.getenv("IMAGE_STYLE", "vivid")
        image_quality = os.getenv("IMAGE_QUALITY", "standard")
        # print values if desired
        # print(f"promptFinal: " + promptFinal)        
        # print(f"deployment = " + deployment)
        # print(f"image_size = " + image_size)
        # print(f"image_n = " + str(image_n))
        # print(f"image_style = " + image_style)
        # print(f"image_quality = " + image_quality)
        #
        #endpoint and api_version are used in GetClient_IMAGE_GEN()
        # endpoint = os.getenv("AZURE_OPENAI_ENDPOINT_IMAGE_GEN", "https://azure-openai-godservants-test-001.openai.azure.com/")
        # print(f"endpoint = " + endpoint)
        # api_version = os.getenv("OPENAI_API_VERSION_IMAGE_GEN", "2024-04-01-preview")
        # print(f"api_version = " + api_version)        
        #
        emsgOperation = f'creating the IMAGE_GEN client'
        client = GetClient_IMAGE_GEN()
        if client:
            # 
            emsgOperation = f'Creating Image using client.images.create' 
            generation_response = client.images.generate( 
                prompt=promptFinal,
                size=image_size,
                model=deployment,
                n=image_n,
                quality=image_quality
            )
            return generation_response
        else:
            raise NameError(f'client is empty.')
    # catch exceptions
    except ValueError as err_value:
        print(f"ValueError: " + err_value._message)
    except AzureOpenAI.InvalidRequestError as err:
        print(f"AzureOpenAI.InvalidRequestError: " + err._message)
    except Exception as e:
        print(f'Exception ' + emsgOperation + f' ' + emsgContext + f': ' + repr(e))
        
    
def GetClient_IMAGE_GEN():
    emsgContext = f'in Client.GetClient_IMAGE_GEN(...)'
    emsgOperation = f''
    client = None
    try:
        emsgOperation = f"getting the AZURE_OPENAI_ENDPOINT_IMAGE_GEN environmental variable"
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT_IMAGE_GEN")
        emsgOperation = f"getting the AZURE_OPENAI_API_KEY_IMAGE_GEN environmental variable"
        key = os.getenv("AZURE_OPENAI_API_KEY_IMAGE_GEN")
        emsgOperation = f"getting the AZURE_OPENAI_API_VERSION_IMAGE_GEN environmental variable"
        version = os.getenv("AZURE_OPENAI_API_VERSION_IMAGE_GEN")
        emsgOperation = f"constructing an AzureOpenAI client object"
        client = AzureOpenAI(
            api_version=version,
            azure_endpoint = endpoint, 
            api_key=key)
        if client is None:
            raise NameError
    except NameError as e:
        print(f'NameError Exception ' + emsgOperation + ' ' + emsgContext + f': ' + repr(e))
    except Exception as e:
        print(f'Exception ' + emsgOperation + f' ' + emsgContext + f': ' + repr(e))
    finally:
        return client
    
