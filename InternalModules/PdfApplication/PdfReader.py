from pypdf import PdfReader

def extract_text(path: str, mode: str = "plain") -> str:
    ret = None
    emsgContext = f'in PdfReader.extract_text()'
    emsgOperation = f''
    try:
        if path is not None:
            #
            emsgOperation = f"constructing a PdfReader object"
            reader = PdfReader(path)
            #
            emsgOperation = f"getting the number of pages in the pdf file"
            number_of_pages = reader.get_num_pages()
            ret = f""
            #
            emsgOperation = f"iterating through the pages"
            for page_index in range(number_of_pages):
                emsgOperation = f"getting page " + str(page_index + 1)
                page = reader.pages[page_index]
                #
                emsgOperation = f"extracting the text from page " + str(page_index + 1)
                ret += f"\n" + page.extract_text(extraction_mode=mode)            
        else: raise NameError
    except NameError as e:
        print(f'NameError Exception ' + emsgOperation + ' ' + emsgContext + f': ' + repr(e))
    except Exception as e:
        print(f'Exception ' + emsgOperation + f' ' + emsgContext + f': ' + repr(e) )
    finally:
        return ret
    

