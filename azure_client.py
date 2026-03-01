from openai import AzureOpenAI
import os
from dotenv import load_dotenv

load_dotenv()


def get_client():
    return AzureOpenAI(
        api_key=os.getenv("AZURE_OPENAI_KEY"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    )


def get_deployment():
    return os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_ID")
