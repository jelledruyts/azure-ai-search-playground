import openai
import os
import re
import logging
from tenacity import retry, wait_random_exponential, stop_after_attempt  

class TextEmbedder():
    openai.api_type = "azure"    
    openai.api_key = os.getenv("AZURE_OPENAI_API_KEY")
    openai.api_base = f"https://{os.getenv('AZURE_OPENAI_SERVICE_NAME')}.openai.azure.com/"
    openai.api_version = os.getenv("AZURE_OPENAI_API_VERSION")

    def clean_text(self, text, truncate_text=False, text_limit=7000):
        # Clean up text (e.g. line breaks, )    
        text = re.sub(r'\s+', ' ', text).strip()
        text = re.sub(r'[\n\r]+', ' ', text).strip()
        # Truncate text if necessary (e.g. for, ada-002, 4095 tokens ~ 7000 chracters)    
        if truncate_text and len(text) > text_limit:
            logging.warning(f"Token limit reached exceeded maximum length ({len(text)} > {text_limit}), truncating...")
            text = text[:text_limit]
        return text

    @retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(6))
    def embed_content(self, text, embedding_deployment_name, clean_text=True, use_single_precision=True):
        embedding_precision = 9 if use_single_precision else 18
        if clean_text:
            text = self.clean_text(text)
        response = openai.Embedding.create(input=text, engine=embedding_deployment_name)
        embedding = [round(x, embedding_precision) for x in response['data'][0]['embedding']]
        return embedding