import os
import json
import base64

from flask import (Flask, redirect, render_template, request,
                   send_from_directory, url_for, jsonify)
from flask_cors import CORS, cross_origin

from markupsafe import escape

import InternalModules.ChatApplication.ProblemSummaryChatCompletion as ProblemSummaryChatCompletion
import InternalModules.RagApplication.ChatCompletion_RAG as ChatCompletion_RAG
import InternalModules.ImageGeneration.ImageGeneration as ImageGeneration

app = Flask(__name__)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

# To run this application run the following commands in the terminal:
# > flask run
#   Go to the url that is displayed
# 
# This is no longer needed
# > az login
#   Enter credentials for Azure
# 

@app.route('/')
def index():
   msg = 'Request for home path received'
   print(msg)
   return msg

@app.route('/api/generate/chat', methods=['GET', 'POST'])
@cross_origin(allow_headers=['Content-Type'])
def chat():
   chat_results_obj = None
   emsgContext = f"/api/generate/chat"
   emsgOperation = f""
   try:
      emsgOperation = f"validating the JSON of the request"
      if request.json:
         #
         emsgOperation = f"getting the prompt from the request"
         input_user = request.json["prompt"]
         if(input_user):
            #
            emsgOperation = f"calling ChatCompletion_RAG.CreateContextAndUseInputThenCompleteChat(prompt = " + input_user + f")"
            chat_results = ChatCompletion_RAG.CreateContextAndUseInputThenCompleteChat(input_user)
            if chat_results:
               #
               if chat_results.text:
                  emsgOperation = f"converting the chat_results.text to an object"
                  chat_results_obj = json.loads(chat_results.text)
               else:
                  raise Exception( f"The return content is empty." )
            else:
               raise Exception( f"The return content is empty." )
         else:
            raise Exception( f"The return content is empty." )
      else:
         raise Exception( f"The return content is empty." )
   except Exception as e:
      chat_results_obj = f"Exception in " + emsgContext + f" while " + emsgOperation + f": " + str({e})
   finally:      
      #
      response = jsonify({"message": "Received", "data": chat_results_obj}) 
      if response:
         #    
         response.headers["Content-Type"] = "application/json"
         #
         return response  


@app.route('/api/generate/image', methods=['GET', 'POST'])
@cross_origin(allow_headers=['Content-Type'])
def generate_image():
   results_obj = None
   emsgContext = f"/api/generate/image"
   emsgOperation = f""
   try:
      emsgOperation = f"validating the JSON of the request"
      if request.json:
         #
         emsgOperation = f"getting the prompt from the request"
         input_user = request.json["prompt"]
         if(input_user):
            
            emsgOperation = f"calling ImageGeneration.create(prompt = " + input_user + f")"
            results = ImageGeneration.create(input_user)
            if results:
               #
               emsgOperation = f"getting the model dump json from the results"
               # Retrieve the generated image
               json_model_dump = results.model_dump_json()
               if json_model_dump:
                  emsgOperation = f"converting the model dump json to an object"
                  results_obj = json.loads(json_model_dump)['data'][0]
               else:
                  raise Exception(f"json_model_dump is empty.")
            else:
               raise Exception( f"The return content is empty." )
         else:
            raise Exception( f"The return content is empty." )
      else:
         raise Exception( f"The return content is empty." )
   except Exception as e:
      results_obj = f"Exception in " + emsgContext + f" while " + emsgOperation + f": " + str({e}) 
   finally:
      #
      response = jsonify({"message": "Received", "data": results_obj}); 
      if response:
         #    
         response.headers["Content-Type"] = "application/json"
         #
         return response        

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

if __name__ == '__main__':
   app.run()
