"""
Generate multimodal embeddings using Azure OpenAI GPT-4o with Vision.
"""

import base64
import os
from openai import AzureOpenAI
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class MultimodalEmbeddings:
    """Generate embeddings for text and images using GPT-4o."""
    
    def __init__(self, azure_endpoint: str, api_key: str, api_version: str = "2024-08-01-preview"):
        self.client = AzureOpenAI(
            azure_endpoint=azure_endpoint,
            api_key=api_key,
            api_version=api_version
        )
        self.deployment_name = "gpt-4o"  # Your GPT-4o deployment name
    
    def encode_text(self, text: str) -> list[float]:
        """Generate text embeddings using GPT-4o."""
        try:
            response = self.client.embeddings.create(
                model=self.deployment_name,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"❌ Error generating text embedding: {e}")
            return []
    
    def encode_image(self, image_path: str) -> list[float]:
        """Generate image embeddings using GPT-4o Vision."""
        try:
            # Load and encode image
            with open(image_path, "rb") as image_file:
                image_data = base64.b64encode(image_file.read()).decode("utf-8")
            
            # Get embeddings via GPT-4o Vision
            # Note: Azure OpenAI doesn't have a direct image embedding endpoint yet
            # We use GPT-4o Vision to generate a description, then embed that
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Describe this image in detail for semantic search purposes. Include objects, colors, composition, mood, and context."
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_data}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=500
            )
            
            description = response.choices[0].message.content
            
            # Generate embedding from description
            return self.encode_text(description), description
            
        except Exception as e:
            print(f"❌ Error generating image embedding: {e}")
            return [], ""
    
    def encode_image_direct(self, image_path: str) -> list[float]:
        """
        Alternative: Use Azure Computer Vision Image Retrieval API
        for native image embeddings (recommended for production).
        
        Requires: Azure Computer Vision resource with Image Retrieval enabled.
        """
        # TODO: Implement Azure Computer Vision vectorizeImage API
        # https://learn.microsoft.com/en-us/azure/ai-services/computer-vision/how-to/image-retrieval
        pass


def get_embeddings_client(endpoint: str = None, api_key: str = None) -> MultimodalEmbeddings:
    """Factory function to create embeddings client from env vars."""
    endpoint = endpoint or os.getenv("AZURE_OPENAI_ENDPOINT")
    api_key = api_key or os.getenv("AZURE_OPENAI_API_KEY")
    
    if not endpoint or not api_key:
        raise ValueError("Azure OpenAI endpoint and API key required")
    
    return MultimodalEmbeddings(endpoint, api_key)
