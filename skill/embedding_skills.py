from .baseskill import TextSkill
from azure.search.documents.indexes.models import (
    AzureOpenAIEmbeddingSkill, OutputFieldMappingEntry
)
import os
from dotenv import load_dotenv

load_dotenv()

class AzureOpenAIEmbeddingSkillTest(TextSkill):
    def __init__(self, resource_uri: str = None, deployment_id: str = None, dimensions: int = None):
        super().__init__("AzureOpenAIEmbeddingSkill")
        self.api_key = os.environ.get("AOAI_API_KEY")
        self.resource_uri = resource_uri or os.environ.get("AOAI_RESOURCE_URI")
        self.deployment_id = deployment_id or os.environ.get("AOAI_DEPLOYMENT_ID", "text-embedding-ada-002")
        self.has_vector_output = True
        self.vector_dimensions = dimensions or int(os.environ.get("AOAI_EMBEDDING_DIMENSIONS", "1536"))
        self.outputs = [
            OutputFieldMappingEntry(name="embedding", target_name="vector_output")
        ]
    
    def create_skill(self):
        if not self.resource_uri:
            raise ValueError("Azure OpenAI resource URI is required")
        
        return AzureOpenAIEmbeddingSkill(
            resource_uri=self.resource_uri,
            deployment_id=self.deployment_id,
            api_key=self.api_key,
            model_name=self.deployment_id,
            dimensions=self.vector_dimensions,
            inputs=self.inputs,
            outputs=self.outputs
        )
