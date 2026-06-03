import os

os.environ['OPENAI_TYPE'] = 'azure'
os.environ['AZURE_SUBSCRIPTION_ID'] = '511700a2-be8e-48ce-84c8-d1c480d9bf53'
# USEAST
os.environ['AZURE_OPENAI_ENDPOINT'] = 'https://abundantstreamssvcs-openai.openai.azure.com/'
os.environ['AZURE_OPENAI_API_VERSION'] = '2024-05-01-preview'
os.environ['AZURE_OPENAI_TEXT_DEPLOYMENT'] = 'gpt-4' 
os.environ['AZURE_OPENAI_TEXT_MODEL'] = 'gpt-4'
os.environ['AZURE_OPENAI_TEXT_TOKEN_RATE_LIMIT'] = '1000'
os.environ['AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT'] = 'text-embedding-ada-002'
os.environ['AZURE_OPENAI_EMBEDDINGS_MODEL'] = 'text-embedding-ada-002'