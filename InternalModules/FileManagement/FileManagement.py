import json
from os import listdir, makedirs
from os.path import isfile, join, exists, splitext, split
import InternalModules.PdfApplication.PdfReader as PdfReader

def get_file_paths(target_folders):
    file_paths = []
    for folder in target_folders:        
        onlyfiles = [f for f in listdir(folder) if isfile(join(folder, f))]
        for file in onlyfiles:
            file_paths.append(join(folder, file))
    return file_paths

def split_text_into_chunks(text, max_length, min_length):
    words = text.split()
    chunks = []
    current_chunk = []

    for word in words:
        current_chunk.append(word)
        if len(' '.join(current_chunk)) < max_length and len(' '.join(current_chunk)) > min_length:
            chunks.append(' '.join(current_chunk))
            current_chunk = []

    # If the last chunk didn't reach the minimum length, add it anyway
    if current_chunk:
        chunks.append(' '.join(current_chunk))

    return chunks

def split_text_into_chunks_by_sentences(text):
    words = text.split()
    chunks = []
    current_chunk = []

    for word in words:        
        if (word.find(f".") > -1):
            word_split = word.split(f".")            
            if((len(word_split) > 1)
            	and ((word_split[0].isnumeric() == False) 
                or (word_split[1].isnumeric() == False))
                ):
                word_for_chunk = word_split[0].strip()
                if ((word_for_chunk) and (len(word_for_chunk) > 0)):
                    current_chunk.append(word_for_chunk)
                    word_for_chunk = '' # empty this so it doesn't get re-added later at the end of the loop
                chunks.append(' '.join(current_chunk))
                current_chunk = []
                word2_for_chunk = word_split[1].strip()
                if ((word2_for_chunk) and (len(word2_for_chunk) > 0)):
                    current_chunk.append(word2_for_chunk)
            else:
                word_for_chunk = word.strip()
        else:
            word_for_chunk = word.strip()
        #
        if ((word_for_chunk) and (len(word_for_chunk) > 0)):
            current_chunk.append(word_for_chunk)

    # If the last chunk didn't wasn't added, add it.
    if current_chunk:
        chunks.append(' '.join(current_chunk))

    return chunks

def create_json_file_from_text(target_folders: list, output_folder: str, output_file_name: str) -> dict:
    json_content = None
    emsgContext = f'in FileManagement.CreateJsonFileFromText(target_folders)'
    emsgOperation = f''
    try:
        emsgOperation = f'validating target_folders parameter'
        if target_folders is not None:
            emsgOperation = f'getting the file paths from the target folders'
            file_paths = get_file_paths(target_folders)
            if file_paths:
                extension_pdf = f".pdf"
                pdf_mode = f"layout"
                json_content = {"messages": []}
                emsgOperation = f'iterating the file paths'
                for path in file_paths:
                    #
                    emsgOperation = f"getting the path's extention"
                    path_ext = splitext(path)[1]
                    if path_ext == extension_pdf:
                        emsgOperation = f"extracting the text from pdf file: " + path
                        file_content = PdfReader.extract_text(path, pdf_mode)
                        emsgOperation = f"forming json_message from pdf file content"
                        json_message = {"role":"assistant", "content": file_content}
                        emsgOperation = f"appending json_message from pdf file content to messages"
                        json_content["messages"].append(json_message)
                    else:
                        emsgOperation = f'opening file to read (' + path + ')'
                        with open(path, 'r', encoding='utf-8') as file:
                            emsgOperation = f'reading file (' + path + ')'
                            file_content = file.read()
                            emsgOperation = f"forming json_message"
                            json_message = {"role":"assistant", "content": file_content}
                            emsgOperation = f"appending json_message to messages"
                            json_content["messages"].append(json_message)
                emsgOperation = f"creating the output_folder (" + output_folder + f") if it doesn't exist"
                if not exists(output_folder): 
                    emsgOperation = f"creating folder (" + output_folder + f")"
                    print(emsgOperation)
                    makedirs(output_folder)
                emsgOperation = f"joining the output_folder to the output_file_name"
                output_file_path = join(output_folder, output_file_name)
                emsgOperation = f"opening file to write (" + output_file_path + ")" 
                with open(output_file_path, "w") as outfile:
                    emsgOperation = f"writing content to (" + output_file_path + ")" 
                    json.dump(json_content, outfile)                       
            else: raise NameError
        else: raise NameError
    except NameError as e:
        print(f'NameError Exception ' + emsgOperation + ' ' + emsgContext + f': ' + repr(e))
    except Exception as e:
        print(f'Exception ' + emsgOperation + f' ' + emsgContext + f': ' + repr(e) )
    finally:
        return json_content
    
def create_json_files_from_text(target_folders: list, output_folder: str) -> dict:
    json_files = []
    emsgContext = f'in FileManagement.CreateJsonFileFromText(target_folders)'
    emsgOperation = f''
    try:
        emsgOperation = f'validating target_folders parameter'
        if target_folders is not None:
            emsgOperation = f'getting the file paths from the target folders'
            file_paths = get_file_paths(target_folders)
            if file_paths:
                #
                emsgOperation = f"creating the output_folder (" + output_folder + f") if it doesn't exist"
                if not exists(output_folder): 
                    emsgOperation = f"creating folder (" + output_folder + f")"
                    print(emsgOperation)
                    makedirs(output_folder)
                extension_pdf = f".pdf"
                extension_jsonl = f".jsonl"
                pdf_mode = f"layout"
                #
                emsgOperation = f'iterating the file paths'
                for path in file_paths:
                    json_content = {"messages": []}
                    #
                    emsgOperation = f"getting the path's tail"
                    path_split = split(path)
                    path_tail = path_split[1]
                    #
                    emsgOperation = f"getting the path's extention"
                    path_splitext = splitext(path_tail)
                    filename_root = path_splitext[0]
                    path_ext = path_splitext[1]
                    if path_ext == extension_pdf:
                        emsgOperation = f"extracting the text from pdf file: " + path
                        file_content = PdfReader.extract_text(path, pdf_mode)
                        emsgOperation = f"forming json_message from pdf file content"
                        json_message = {"role":"assistant", "content": file_content}
                        emsgOperation = f"appending json_message from pdf file content to messages"
                        json_content["messages"].append(json_message)
                    else:
                        emsgOperation = f'opening file to read (' + path + ')'
                        with open(path, 'r', encoding='utf-8') as file:
                            emsgOperation = f'reading file (' + path + ')'
                            file_content = file.read()
                            emsgOperation = f"forming json_message"
                            json_message = {"role":"assistant", "content": file_content}
                            emsgOperation = f"appending json_message to messages"
                            json_content["messages"].append(json_message)
                    #
                    output_file_name = filename_root + f"_" + path_ext[1:] + extension_jsonl
                    #
                    emsgOperation = f"joining the output_folder to the output_file_name"
                    output_file_path = join(output_folder, output_file_name)
                    #
                    emsgOperation = f"opening file to write (" + output_file_path + ")" 
                    with open(output_file_path, "w") as outfile:
                        #
                        emsgOperation = f"writing content to (" + output_file_path + ")" 
                        json.dump(json_content, outfile) 
                    #
                    emsgOperation = f"appending the filepath and contents to json_files"
                    json_files.append({"filepath":output_file_path, "content": file_content})                      
            else: raise NameError
        else: raise NameError
    except NameError as e:
        print(f'NameError Exception ' + emsgOperation + ' ' + emsgContext + f': ' + repr(e))
    except Exception as e:
        print(f'Exception ' + emsgOperation + f' ' + emsgContext + f': ' + repr(e) )
    finally:
        return json_files