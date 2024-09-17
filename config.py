import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Read API key and Base URL from environment variables
GPT_API_KEY = os.getenv('OPENAI_API_KEY')
GPT_API_BASEURL = os.getenv('OPENAI_BASEURL', 'https://api.openai.com/v1')

if not GPT_API_KEY:
    raise EnvironmentError("OPENAI_API_KEY environment variable is not set.")

def get_gpt_api_url(endpoint):
    return f"{GPT_API_BASEURL}/{endpoint}"

