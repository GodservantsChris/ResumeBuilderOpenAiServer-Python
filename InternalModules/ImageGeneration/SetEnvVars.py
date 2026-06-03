import os

os.environ['AZURE_OPENAI_ENDPOINT_IMAGE_GEN'] = 'https://abund-mlzcebfy-swedencentral.cognitiveservices.azure.com/openai/deployments/gpt-image-1.5/images/generations?api-version=2025-04-01-preview'
os.environ['AZURE_OPENAI_API_VERSION_IMAGE_GEN'] = '2025-04-01-preview'
os.environ['DEPLOYMENT_NAME_IMAGE_GEN'] = 'gpt-image-1.5'
os.environ['IMAGE_SIZE'] = '1024x1024'
os.environ['IMAGE_N'] = '1'
os.environ['IMAGE_QUALITY'] = 'medium'
