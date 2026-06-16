import os
import json
from openai.types.chat import ChatCompletion

import InternalModules.OpenAiEnvironment.AzureAiClient as AzureAiClient
import InternalModules.OpenAiEnvironment.AzureAiFunctions as AzureAiFunctions

def ChatCompletion(client, colMessages, temperature_level = None, 
                   functions_collection = None, function_call_arg = None,
                   withRawResponse = False) ->  ChatCompletion:

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
                             withRawResponse = False) ->  ChatCompletion:
    response = None
    emsgContext = f'in AzureAiClient.GetClientAndCompleteChat(...)'
    emsgOperation = f''
    try:
        emsgOperation = f'getting the client'        
        client = AzureAiClient.GetClient()        
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
                                         available_functions) ->  ChatCompletion:
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

    
