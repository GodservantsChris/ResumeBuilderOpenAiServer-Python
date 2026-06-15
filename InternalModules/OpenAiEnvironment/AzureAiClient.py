import os
from openai import AzureOpenAI
import time
import json
import datetime
import requests
from azure.cosmos import CosmosClient

import InternalModules.OpenAiEnvironment.SetEnvVars as SetEnvVars
import InternalModules.OpenAiEnvironment.AzureAiFunctions as AzureAiFunctions
import InternalModules.FileManagement.FileManagement as FileManagement

def GetClient():
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
        emsgOperation = f"constructing an AzureOpenAI client object"
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
    
def ChatCompletion(client, colMessages, temperature_level = None, 
                   functions_collection = None, function_call_arg = None,
                   withRawResponse = False):

    response = None
    emsgContext = f'in Client.ChatCompletion(...)'
    emsgOperation = f''
    try:
        emsgOperation = f"validating the client arg"
        if client is not None:
            emsgOperation = f"validating the colMessages arg"
            if colMessages is not None:  
                fTemperature = None
                if temperature_level is not None:
                    emsgOperation = f"converting the temperature_level arg to a float"  
                    fTemperature = float(temperature_level)
                emsgOperation = f"getting the AZURE_OPENAI_TEXT_DEPLOYMENT environmental variable"
                deployment_text=os.getenv("AZURE_OPENAI_TEXT_DEPLOYMENT")
                emsgOperation = f"getting the AZURE_OPENAI_TEXT_TOKEN_RATE_LIMIT environmental variable"
                tokens_max=os.getenv("AZURE_OPENAI_TEXT_TOKEN_RATE_LIMIT")
                emsgOperation = f"converting the the AZURE_OPENAI_TEXT_TOKEN_RATE_LIMIT environmental variable  to an int"
                iMaxTokenRate = int(tokens_max)
                emsgOperation = f"creating the chat completion using the client"
                if withRawResponse: 
                    emsgOperation += f" with raw response"
                    response = client.chat.completions.with_raw_response.create(
                        model=deployment_text,
                        temperature=fTemperature,
                        max_tokens=iMaxTokenRate,
                        messages=colMessages,
                        functions=functions_collection,
                        function_call=function_call_arg
                    )
                else:
                    response = client.chat.completions.create(
                        model=deployment_text,
                        temperature=fTemperature,
                        max_tokens=iMaxTokenRate,
                        messages=colMessages,
                        functions=functions_collection,
                        function_call=function_call_arg
                    )
                if response:
                    return response
                else:
                    raise NameError(f"The response object is None.")
            else: raise NameError
        else: raise NameError
    except NameError as e:
        raise Exception(f'NameError Exception ' + emsgOperation + ' ' + emsgContext + f': ' + repr(e))
    except Exception as e:
        raise Exception(f'Exception ' + emsgOperation + f' ' + emsgContext + f': ' + repr(e) )
    
def GetClientAndCompleteChat(colMessages, temperature_level, 
                             functions_collection = None, function_call_arg = None,
                             withRawResponse = False):
    response = None
    emsgContext = f'in AzureAiClient.GetClientAndCompleteChat(...)'
    emsgOperation = f''
    try:
        emsgOperation = f'getting the client'        
        client = GetClient()        
        if client is not None:
            emsgOperation = f'validating the colMessages parameter'
            if colMessages is not None:                
                emsgOperation = f'completing the chat'
                response = ChatCompletion(client, colMessages, temperature_level, 
                                          functions_collection, function_call_arg,
                                          withRawResponse)
                if response:
                    return response
                else:
                    raise NameError
            else: raise NameError
        else: raise NameError
    except NameError as e:
        raise Exception(f'NameError Exception ' + emsgOperation + ' ' + emsgContext + f': ' + repr(e))
    except Exception as e:
        raise Exception(f'Exception ' + emsgOperation + f' ' + emsgContext + f': ' + repr(e) )

"""
GetClientAndCompleteChatWithFunction(...) currently only supports a functions_collection with one function item
"""   
def GetClientAndCompleteChatWithFunction(colMessages, temperature_level, 
                                         functions_collection,
                                         available_functions):
    response_final = None
    emsgContext = f'in AzureAiClient.GetClientAndCompleteChatWithFunction(...)'
    emsgOperation = f''
    try:
        emsgOperation = f'validating the functions collection'
        if functions_collection is not None:
            emsgOperation = f'completing the original chat'        
            original_response = GetClientAndCompleteChat(colMessages, temperature_level, functions_collection)
            emsgOperation = f'validating the original response'
            if original_response is not None:
                #
                emsgOperation = f'getting the message from the first choice of the original response'
                response_message = original_response.choices[0].message
                emsgOperation = f'validating the message from the first choice of the original response'
                if response_message is not None:
                    emsgOperation = f'getting the role from the message of the first choice of the original response'
                    response_message_role = response_message.role
                    emsgOperation = f'getting the function_call from the message of the first choice of the original response'
                    response_message_function_call = response_message.function_call
                    emsgOperation = f'validating the function_call from the message of the first choice of the original response'
                    if response_message_function_call is not None:
                        emsgOperation = f'getting the name from the function_call'
                        recommended_function_name = response_message_function_call.name
                        emsgOperation = f'validating the name from the function_call'
                        if recommended_function_name is not None:
                            emsgOperation = f'getting the arguments from the function_call'
                            response_message_arguments = response_message_function_call.arguments
                            emsgOperation = f'validating the arguments from the function_call'
                            if response_message_arguments is not None:
                                emsgOperation = f'converting the arguments from the function_call to JSON'
                                json_response_arguments = json.loads(response_message_arguments)
                                emsgOperation = f'validating the JSON object after converting the arguments from the function_call to JSON'
                                if json_response_arguments is not None:
                                    #
                                    emsgOperation = 'getting the recommended function to call'
                                    function_to_call = available_functions[recommended_function_name]
                                    emsgOperation = 'validating the recommended function to call'
                                    if function_to_call is not None:
                                        emsgOperation = 'calling the recommended function and storing the response'
                                        response_string = function_to_call(**json_response_arguments)
                                        #
                                        emsgOperation = f'updating the messages to include the function, arguments and response'
                                        colMessages = AzureAiFunctions.AppendFunctionMessages(colMessages, 
                                                                                            response_message_role, 
                                                                                            recommended_function_name, 
                                                                                            response_message_arguments,
                                                                                            response_string)
                                        emsgOperation = f'validating the updated messages'
                                        if colMessages is not None:
                                            #
                                            emsgOperation = f're-running the chat completion'
                                            response_final = GetClientAndCompleteChat(colMessages, "0.0", functions_collection, "auto")
                                            emsgOperation = f'validating the final response'
                                            if response_final:
                                                return response_final
                                            else:
                                                raise NameError
                                        else: raise NameError
                                    else: raise NameError                                        
                                else: raise NameError
                            else: raise NameError
                        else: raise NameError
                    else: raise NameError
                else: raise NameError
            else: raise NameError
        else: raise NameError
    except NameError as e:
        raise Exception(f'NameError Exception ' + emsgOperation + ' ' + emsgContext + f': ' + repr(e))
    except Exception as e:
        raise Exception(f'Exception ' + emsgOperation + f' ' + emsgContext + f': ' + repr(e) )

""" Embeddings """   
def CreateEmbeddings(text):
    embeddings = None
    emsgContext = f''
    emsgOperation = f''
    try:
        emsgOperation = f"getting the client object"
        client = GetClient()
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

def CreateEmbedding(text, client, deployment):
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
    
""" File Management """
def UploadFiles(client, files, upload_purpose="assistants") -> list:
    files_uploaded = []
    emsgContext = f'in AzureAiClient.UploadFineTuningFiles(...)'
    emsgOperation = f''
    try:
        emsgOperation = f'validating the files parameter'
        if files is not None:             
            emsgOperation = f'validating the AzureOpenAI object as client'
            if client is not None:     
                emsgOperation = f'iterating the files collection'
                for file in files:
                    emsgOperation = f"Opening file: {file}"
                    opened_file =  open(file, "rb")
                    if opened_file is not None:
                        emsgOperation = f"creating the file in the AzureOpenAI client"
                        response = client.files.create(
                            file = opened_file, purpose=upload_purpose
                        )
                        emsgOperation = f"validating the response for file {file}"
                        if response is not None:
                            emsgOperation = f"getting the response.id for file {file}"
                            file_id = response.id
                            if file_id:
                                file_item = {"file_name": file, "file_id" : file_id}
                                files_uploaded.append(file_item)
                            else: raise NameError
                        else: raise NameError        
                    else: raise NameError
                #
                return files_uploaded
            else: raise NameError
        else: raise NameError
    except NameError as e:
        raise Exception(f'NameError Exception ' + emsgOperation + ' ' + emsgContext + f': ' + repr(e))
    except Exception as e:
        raise Exception(f'Exception ' + emsgOperation + f' ' + emsgContext + f': ' + repr(e))
        

def UploadFineTuningFiles(client, files) -> list:
    return UploadFiles(client, files, "fine-tune")

def GetClientAndUploadFiles(target_folders, purpose="assistants"):
    files_uploaded = None
    emsgContext = f'in AzureAiClient.GetClientAndUploadFiles(...)'
    emsgOperation = f''
    try:
        emsgOperation = f'validating the target_folders parameter'
        if target_folders is not None:  
            emsgOperation = f"getting the file paths from the target folders"
            files = FileManagement.get_file_paths(target_folders)
            emsgOperation = f'validating the files collection'
            if files is not None:
                emsgOperation = f'constructing an AzureOpenAI object as client'
                client = GetClient() 
                emsgOperation = f'validating the AzureOpenAI object as client'
                if client is not None:     
                    emsgOperation = f'uploading the files'
                    files_uploaded = UploadFiles(client, files, purpose)
                    if files_uploaded:
                        return files_uploaded
                    else:
                        raise NameError
                else: raise NameError
            else: raise NameError
        else: raise NameError
    except NameError as e:
        raise Exception(f'NameError Exception ' + emsgOperation + ' ' + emsgContext + f': ' + repr(e))
    except Exception as e:
        raise Exception(f'Exception ' + emsgOperation + f' ' + emsgContext + f': ' + repr(e))
        

def GetFileIds(client : AzureOpenAI, purpose = None) -> dict:
    file_ids = None
    emsgContext = f'in AzureAiClient.GetFileIds()'
    emsgOperation = f''
    try:
        emsgOperation = f"validating the client parameter"
        if client is not None:
            emsgOperation = f"getting the list of files"
            response = client.files.list()
            emsgOperation = f"validating the response"
            if response:
                file_ids = dict()
                emsgOperation = f"building file_ids by iterating the list of files"
                for document in response.data:
                    if document.purpose == purpose:
                        file_ids[document.filename] = document.id
                return file_ids
            else: raise NameError
        else: raise NameError
    except NameError as e:
        raise Exception(f'NameError Exception ' + emsgOperation + ' ' + emsgContext + f': ' + repr(e))
    except Exception as e:
        raise Exception(f'Exception ' + emsgOperation + f' ' + emsgContext + f': ' + repr(e) )        

def RetrieveFileContents(client : AzureOpenAI, file_ids : dict) -> str:
    file_contents = {}
    emsgContext = f'in AzureAiClient.RetrieveFileContents(file_ids)'
    emsgOperation = f''
    try:
        emsgOperation = f"validating the client parameter"
        if client is not None:
            emsgOperation = f"validating the file_ids parameter"
            if file_ids is not None:
                emsgOperation = f"iterating the file_ids dictionary values"
                for id in file_ids.values():
                    emsgOperation = f"getting the content of the current id"
                    response = client.files.content(id)
                    emsgOperation = f"validating the response from getting the content of the current id"
                    if response:
                        emsgOperation = f"getting the text from the response"
                        file_contents[id] = response.text
                    else: raise NameError
                return file_contents
            else: raise NameError
        else: raise NameError
    except NameError as e:
        raise Exception(f'NameError Exception ' + emsgOperation + ' ' + emsgContext + f': ' + repr(e))
    except Exception as e:
        raise Exception(f'Exception ' + emsgOperation + f' ' + emsgContext + f': ' + repr(e) )

def RetrieveFileContentsCombined(client : AzureOpenAI, file_ids : dict, roles=["system", "user", "assistant"]) -> str:
    file_contents = {}
    emsgContext = f'in AzureAiClient.RetrieveFileContents(file_ids)'
    emsgOperation = f''
    try:
        emsgOperation = f"validating the client parameter"
        if client is not None:
            emsgOperation = f"validating the file_ids parameter"
            if file_ids is not None:
                emsgOperation = f"iterating the file_ids dictionary values"
                for id in file_ids.values():
                    emsgOperation = f"getting the content of the current id"
                    response = client.files.content(id)
                    emsgOperation = f"validating the response from getting the content of the current id"
                    if response:
                        emsgOperation = f"processing the response's text"
                        response_dict = response.text.strip("'").split('\r\n{')
                        emsgOperation = f"combining the text from the response"
                        response_combined = ''
                        for i in response_dict:  #'list' object has no attribute 'values' 
                            emsgOperation = f"processing an item from the response's processed text collection"
                            i = i.strip("'")
                            if i.startswith('{') == False:
                                i = '{' + i
                            i = i[14:(len(i) - 2)]
                            i = i.split('}, ')
                            content_substring = ', "content": '
                            for j in i:
                                rolename = '"system"'
                                roleindex = len('"role": ') + len(rolename)
                                for rolenamecandidate in roles:
                                    roleindexsearch = j.find(rolenamecandidate)
                                    if roleindexsearch != -1:
                                        roleindex = roleindexsearch + len(rolenamecandidate)
                                emsgOperation = f"processing an item from the processed text collection's processed item"
                                j = j[(roleindex + len(content_substring)):].strip().strip('}').strip(']').strip('}').strip('"') + ' '
                                response_combined += j
                        emsgOperation = f"setting the file_contents item"
                        file_contents[id] = response_combined
                    else: raise NameError
                return file_contents
            else: raise NameError
        else: raise NameError
    except NameError as e:
        raise Exception(f'NameError Exception ' + emsgOperation + ' ' + emsgContext + f': ' + repr(e))
    except Exception as e:
        raise Exception(f'Exception ' + emsgOperation + f' ' + emsgContext + f': ' + repr(e) )

def DeleteFiles(client : AzureOpenAI, file_ids : dict):
    emsgContext = f'in AzureAiClient.DeleteFiles(file_ids)'
    emsgOperation = f''
    try:
        emsgOperation = f"validating the client parameter"
        if client is not None:
            emsgOperation = f"validating the file_ids parameter"
            if file_ids is not None:
                emsgOperation = f"iterating the file_ids dictionary values"
                for id in file_ids.values():
                    emsgOperation = f"deleting the current id"
                    response = client.files.delete(id)
            else: raise NameError
        else: raise NameError
    except NameError as e:
        raise Exception(f'NameError Exception ' + emsgOperation + ' ' + emsgContext + f': ' + repr(e))
    except Exception as e:
        raise Exception(f'Exception ' + emsgOperation + f' ' + emsgContext + f': ' + repr(e) )

""" Fine Tuning
def GetClient_FineTuning():
    emsgContext = f'in Client.GetClient_FineTuning(...)'
    emsgOperation = f''
    client = None
    try:
        emsgOperation = f"getting the AZURE_OPENAI_FINE_TUNING_ENDPOINT environmental variable"
        endpoint = os.getenv("AZURE_OPENAI_FINE_TUNING_ENDPOINT")
        emsgOperation = f"getting the AZURE_OPENAI_FINE_TUNING_API_KEY environmental variable"
        key = os.getenv("AZURE_OPENAI_FINE_TUNING_API_KEY")
        emsgOperation = f"getting the AZURE_OPENAI_FINE_TUNING_API_VERSION environmental variable"
        version = os.getenv("AZURE_OPENAI_FINE_TUNING_API_VERSION")
        emsgOperation = f"constructing an AzureOpenAI client object"
        client = AzureOpenAI(
            api_version=version,
            azure_endpoint = endpoint, 
            api_key=key)
        if client is None:
            raise NameError
    except NameError as e:
        raise Exception(f'NameError Exception ' + emsgOperation + ' ' + emsgContext + f': ' + repr(e))
    except Exception as e:
        raise Exception(f'Exception ' + emsgOperation + f' ' + emsgContext + f': ' + repr(e))
    finally:
        return client
    
def GetFineTuningClientAndUploadFiles(files) -> list:
    files_uploaded = None
    emsgContext = f'in AzureAiClient.GetClientAndUploadFineTuningFiles(...)'
    emsgOperation = f''
    try:
        emsgOperation = f'validating the files parameter'
        if files is not None:             
            emsgOperation = f'constructing an AzureOpenAI object as client'
            client = GetClient_FineTuning() 
            emsgOperation = f'validating the AzureOpenAI object as client'
            if client is not None:     
                emsgOperation = f'uploading the files'
                files_uploaded = UploadFineTuningFiles(client, files)
            else: raise NameError
        else: raise NameError
    except NameError as e:
        raise Exception(f'NameError Exception ' + emsgOperation + ' ' + emsgContext + f': ' + repr(e))
    except Exception as e:
        raise Exception(f'Exception ' + emsgOperation + f' ' + emsgContext + f': ' + repr(e))
    finally:
        return files_uploaded

def RunFineTuningJob(file_id_training: str, 
                     file_id_validation: str,
                     num_epochs = 3,
                     size_batch = 4,
                     multiplier_learning_rate = 0.1,
                     value_seed = 105
                     ) -> str:
    
    job_id = None
    emsgContext = f'in RunFineTuningJob.Run(...)'
    emsgOperation = f''
    jobs = None
    try:
        emsgOperation = f'validating the file_id_training parameter'
        if file_id_training is not None:             
            emsgOperation = f'validating the file_id_validation parameter'
            if file_id_validation is not None: 
                emsgOperation = f'constructing an AzureOpenAI object as client'
                client = GetClient_FineTuning() 
                emsgOperation = f'validating the AzureOpenAI object as client'
                if client is not None:               
                    emsgOperation = f"getting the client.fine_tuning_job object"
                    jobs = client.fine_tuning.jobs
                    emsgOperation = f"validating the jobs object"                            
                    if jobs is not None:
                        name_model = os.getenv("AZURE_OPENAI_FINE_TUNING_MODEL")
                        #
                        emsgOperation = f'creating the fine tuning job on the the AzureOpenAI object client'
                        response = jobs.create(
                            training_file = file_id_training,
                            validation_file = file_id_validation,
                            model = name_model,
                            hyperparameters={"n_epochs": num_epochs, 
                                             "batch_size": size_batch,
                                             "learning_rate_multiplier": multiplier_learning_rate},
                            seed = value_seed
                        )
                        emsgOperation = f'validating the response from creating the fine tuning job on the the AzureOpenAI object client'
                        if response is not None:
                            job_id = response.id
                        else: raise NameError
                    else: raise NameError
                else: raise NameError
            else: raise NameError
        else: raise NameError
    except NameError as e:
        raise Exception(f'NameError Exception ' + emsgOperation + ' ' + emsgContext + f': ' + repr(e) )
    except Exception as e:
        raise Exception(f'Exception ' + emsgOperation + f' ' + emsgContext + f': ' + repr(e) )
    finally:
        return job_id

def TrackFineTuningJob(job_id: str) -> str:
    fine_tuned_model = None
    emsgContext = f'in TrackFineTuningJob.Run(job_id)'
    emsgOperation = f''
    try:
        emsgOperation = f'validating the job_id parameter'
        if job_id is not None: 
            emsgOperation = f'constructing an AzureOpenAI object as client'
            client = GetClient_FineTuning()  
            emsgOperation = f'validating the AzureOpenAI object as client'
            if client is not None:               
                emsgOperation = f"getting the client.fine_tuning_job object"
                jobs = client.fine_tuning.jobs
                emsgOperation = f"validating the jobs object"
                if jobs is not None:               
                    emsgOperation = f"getting the status of our fine-tuning job"
                    response = jobs.retrieve(job_id)
                    emsgOperation = f"validating the response object"
                    if response is not None:
                        status = response.status
                        # If the job isn't done yet, poll it every 10 seconds.
                        start_time = time.time()
                        emsgOperation = f"getting the AZURE_OPENAI_FINE_TUNING_JOB_POLLING_INTERVAL environmental variable and converting it to float"
                        poll_interval = float(os.getenv("AZURE_OPENAI_FINE_TUNING_JOB_POLLING_INTERVAL"))
                        emsgOperation = f"checking the job status every {poll_interval} seconds"
                        while status not in ["succeeded", "failed"]:
                            time.sleep(poll_interval)
                            #
                            emsgOperation = f"retrieving the response object for the job"
                            response = jobs.retrieve(job_id)
                            print("Elapsed time: {} minutes {} seconds".format(int((time.time() - start_time) // 60), int((time.time() - start_time) % 60)))
                            status = response.status
                            print(f'Status: {status}')
                        print(response.model_dump_json(indent=2))
                        print(f'Fine-tuning job {job_id} finished with status: {status}')
                        # Retrieve and return the fine_tuned_model name
                        fine_tuned_model = response.fine_tuned_model
                    else: raise NameError        
                else: raise NameError
            else: raise NameError
        else: raise NameError
    except NameError as e:
        raise Exception(f'NameError Exception ' + emsgOperation + ' ' + emsgContext + f': ' + repr(e) )
    except Exception as e:
        raise Exception(f'Exception ' + emsgOperation + f' ' + emsgContext + f': ' + repr(e) )
    finally:
        return fine_tuned_model

def DeployFineTunedModel(name_fine_tuned_model, version_fine_tuned_model):
    model_deployment_name = ''
    emsgContext = f'in AzureAiClient.DeployFineTunedModel'
    emsgOperation = f''
    try:
        emsgOperation = f"validating the name_fine_tuned_model arg"
        if name_fine_tuned_model is not None:
            emsgOperation = f"validating the nversion_fine_tuned_model arg"
            if version_fine_tuned_model is not None:
                emsgContext += f"(" + name_fine_tuned_model + f", " + version_fine_tuned_model +  f")"
                emsgOperation = f"gettting the necessary environmental variables"
                version_api = os.getenv("AZURE_OPENAI_FINE_TUNING_API_VERSION")
                token = os.getenv("TEMP_AUTH_TOKEN")
                id_subscription = os.getenv("AZURE_SUBSCRIPTION_ID")
                resource_group = os.getenv("AZURE_OPENAI_FINE_TUNING_RESOURCE_GROUP_NAME")
                resource_name = os.getenv("AZURE_OPENAI_FINE_TUNING_RESOURCE_NAME")
                fine_tuning_model = os.getenv("AZURE_OPENAI_FINE_TUNING_MODEL")
                #
                emsgOperation = f'setting the model_deployment_name with current datetime appended'
                dt_now = datetime.datetime.now()
                str_now = dt_now.strftime("%Y-%m-%d-%H-%M-%S")
                model_deployment_name = fine_tuning_model + "-" + str_now
                #
                emsgOperation = f"setting up deploy_params"            
                deploy_params = {"api-version": version_api}
                emsgOperation = f"re-assigning deploy_params using json.dumps"
                json_deploy_params = json.dumps(deploy_params)
                #
                emsgOperation = f"setting up deploy_headers"            
                deploy_headers = {"content-type": "application/json", "Authorization": "Bearer {}".format(token)}
                emsgOperation = f"re-assigning deploy_headers using json.dumps"
                json_deploy_headers = json.dumps(deploy_headers)
                #
                emsgOperation = f"setting up deploy_data"            
                deploy_data = {"sku": {"name": "standard", "capacity": 1}, "properties": {"model": {"format": "OpenAI","name": name_fine_tuned_model,"version": version_fine_tuned_model}}}
                emsgOperation = f"re-assigning deploy_data using json.dumps"
                json_deploy_data = json.dumps(deploy_data)
                #
                emsgOperation = f"validating deploy_data"
                if deploy_data is not None:
                    #
                    emsgOperation = f"setting request_url"
                    request_url = f"https://management.azure.com/subscriptions/" + id_subscription + f'/resourceGroups/' + resource_group  + f'/providers/Microsoft.CognitiveServices/accounts/' + resource_name + f'/deployments/' + model_deployment_name
                    #
                    emsgOperation = 'sending a request for a new deployment with url: ' + request_url\
                        + '; params = ' + json_deploy_params\
                        + '; headers = ' + json_deploy_headers\
                        + '; data = ' + json_deploy_data
                    response = requests.put(request_url, data=json_deploy_data, params=deploy_params, headers=deploy_headers)
                    if response is not None:
                        print(response)
                        print(response.reason)
                        print(response.json())
                    else: raise NameError
                else: raise NameError
            else: raise NameError
        else: raise NameError
    except NameError as e:
        raise Exception(f'NameError Exception ' + emsgOperation + ' ' + emsgContext  + f": " + repr(e))
        model_deployment_name = None
    except Exception as e:
        raise Exception(f'Exception ' + emsgOperation + f' ' + emsgContext + f": " + repr(e) )
        model_deployment_name = None
    finally:        
        return model_deployment_name
"""

