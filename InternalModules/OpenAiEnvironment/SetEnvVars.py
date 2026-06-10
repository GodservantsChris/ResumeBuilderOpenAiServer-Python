import os

os.environ['OPENAI_TYPE'] = 'azure'
os.environ['AZURE_SUBSCRIPTION_ID'] = 'ff423e87-a552-45d3-be3a-a3a662b074c9'
# USEAST
os.environ['AZURE_OPENAI_ENDPOINT'] = 'https://resumebuilder-openairesource.openai.azure.com/'
os.environ['AZURE_OPENAI_API_VERSION'] = '2025-08-07'
os.environ['AZURE_OPENAI_TEXT_DEPLOYMENT'] = 'gpt-4,1' 
os.environ['AZURE_OPENAI_TEXT_MODEL'] = 'gpt-4.1'
os.environ['AZURE_OPENAI_TEXT_TOKEN_RATE_LIMIT'] = '1000'
os.environ['AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT'] = 'text-embedding-ada-002'
os.environ['AZURE_OPENAI_EMBEDDINGS_MODEL'] = 'text-embedding-ada-002'