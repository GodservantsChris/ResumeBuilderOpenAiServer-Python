from openai import AzureOpenAI

import InternalModules.OpenAiEnvironment.AzureAiClient as AzureAiClient
import InternalModules.FileManagement.FileManagement as FileManagement

def UploadFiles(client, files, upload_purpose="assistants") -> list:
    files_uploaded = []
    emsgContext = f'in AzureAiFileManagement.UploadFineTuningFiles(...)'
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

def GetClientAndUploadFiles(target_folders, purpose="assistants") -> list:
    files_uploaded = None
    emsgContext = f'in AzureAiFileManagement.GetClientAndUploadFiles(...)'
    emsgOperation = f''
    try:
        emsgOperation = f'validating the target_folders parameter'
        if target_folders is not None:  
            emsgOperation = f"getting the file paths from the target folders"
            files = FileManagement.get_file_paths(target_folders)
            emsgOperation = f'validating the files collection'
            if files is not None:
                emsgOperation = f'constructing an AzureOpenAI object as client'
                client = AzureAiClient.GetClient() 
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
    emsgContext = f'in AzureAiFileManagement.GetFileIds()'
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
    emsgContext = f'in AzureAiFileManagement.RetrieveFileContents(file_ids)'
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
    emsgContext = f'in AzureAiFileManagement.RetrieveFileContents(file_ids)'
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

