import os
from openai import AzureOpenAI

import InternalModules.OpenAiEnvironment.SetEnvVars

from InternalModules.OpenAiEnvironment.AzureAiClient import GetClientAndCompleteChat
import InternalModules.OpenAiEnvironment.AzureAiFunctions

# functions
def createPrompt(typeItems, listItemTypes, countItems):
  header = f"These are some problems that might be encountered for the {typeItems} in descending order of frequency of problems."
  prompt = f"Summarize problems when these are not normal : {listItemTypes}. \
    Per item, list {countItems} possible problems in descending order of frequency of problems. \
    Start with this header: {header} and a new line."
  return prompt

def createMessages(titleJob, strPrompt):
  system_context = f"I'm a {titleJob}."
  # set the messages collection
  messages = [
    {"role":"system", "content":system_context},
    {"role": "user", "content": strPrompt},
  ]
  return messages

def processMessages(colMsgs, temperature_level):  
  completion = GetClientAndCompleteChat(colMsgs, temperature_level)
  # return the completion
  return completion.choices[0].message.content

def run(job_title, item_type, list_item_types, no_items):
  system_context = f"I'm a {job_title}."
  messages = createMessages(system_context, createPrompt(item_type, list_item_types, no_items))
  temperature_level = f"0.7"
  return processMessages(messages, temperature_level)