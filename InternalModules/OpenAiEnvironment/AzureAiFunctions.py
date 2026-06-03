def CreateFunctionProperty(property_name, property_type, property_description):
    function_property = None
    emsgContext = f'in AzureAiClient.CreateFunctionProperty(...)'
    emsgOperation = f''
    try:
        emsgOperation = f'validating the property_name parameter'
        if property_name is not None:
            emsgOperation = f'validating the property_type parameter'
            if property_type is not None:
                emsgOperation = f'validating the property_description parameter'
                if property_description is not None:
                    emsgOperation = f'setting the function_property'
                    function_property = {
                        "property_name": property_name,
                        "property_values": {"type": property_type, "description": property_description}
                        }
                else: raise NameError
            else: raise NameError
        else: raise NameError
    except NameError as e:
        print(f'NameError Exception ' + emsgOperation + ' ' + emsgContext + f': ' + repr(e))
    except Exception as e:
        print(f'Exception ' + emsgOperation + f' ' + emsgContext + f': ' + repr(e) )
    finally:
        return function_property

def CreateParameterProperties(function_properties_collection):
    parameter_properties = None
    emsgContext = f'in AzureAiClient.CreateParameterProperties()'
    emsgOperation = f''
    try:
        emsgOperation = f'validating the function_properties_collection parameter'
        if function_properties_collection is not None:
            emsgOperation = f'constructing parameter_properties as a dictionary'
            parameter_properties = dict()
            emsgOperation = f'iterating the function_properties_collection'
            for function_property in function_properties_collection:
                emsgOperation += f' and getting the property_name property'
                cur_property_name = function_property["property_name"]
                emsgOperation += f' and getting the property_values property'
                cur_property_values = function_property["property_values"] # {"type": property_type, "description": property_description}
                emsgOperation += f' and adding the ' + cur_property_name + f' item to the parameter_properties dictionary'
                parameter_properties[cur_property_name] = cur_property_values
        else: raise NameError
    except NameError as e:
        print(f'NameError Exception ' + emsgOperation + ' ' + emsgContext + f': ' + repr(e))
    except Exception as e:
        print(f'Exception ' + emsgOperation + f' ' + emsgContext + f': ' + repr(e) )
    finally:
        return parameter_properties

def CreateFunctionItem(function_name, function_description, parameters_type, parameter_properties, required_properties = None):
    function_item = None
    emsgContext = f'in AzureAiClient.CreateFunctionItem(...)'
    emsgOperation = f''
    try:
        emsgOperation = f'validating the function_name parameter'
        if function_name is not None:
            emsgOperation = f'validating the function_description parameter'
            if function_description is not None:
                emsgOperation = f'validating the function_description parameter'
                if parameters_type is not None:
                    emsgOperation = f'validating the parameters_type parameter'
                    if parameter_properties is not None:
                        itemFunction = {
                            "name":function_name,
                            "description":function_description,
                            "parameters": {
                                "type": parameters_type,
                                "properties": parameter_properties
                            }
                        }
                        if required_properties is not None:
                            itemFunction["parameters"]["required"] = required_properties
                    else: raise NameError
                else: raise NameError
            else: raise NameError
        else: raise NameError
    except NameError as e:
        print(f'NameError Exception ' + emsgOperation + ' ' + emsgContext + f': ' + repr(e))
    except Exception as e:
        print(f'Exception ' + emsgOperation + f' ' + emsgContext + f': ' + repr(e) )
    finally:
        return itemFunction
def AppendFunctionMessages(original_messages: dict, 
                           role_for_function_call: str, 
                           function_name: str, 
                           function_args: dict, 
                           function_response_string: str):
    final_messages = original_messages
    final_messages.append( # adding assistant response to messages
        {
            "role": role_for_function_call,
            "function_call": {
                "name": function_name,
                "arguments": function_args,
            },
            "content": None
        }
    )
    final_messages.append( # adding function response to messages
        {
            "role": "function",
            "name": function_name,
            "content": function_response_string,
        }
    )
    return final_messages
