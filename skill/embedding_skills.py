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
        # now dotenv is loaded, these picks up from your .env
        self.resource_uri = resource_uri or os.environ.get("AOAI_RESOURCE_URI")
        self.deployment_id = deployment_id or os.environ.get("AOAI_DEPLOYMENT_ID", "text-embedding-ada-002")
        self.has_vector_output = True
        self.vector_dimensions = dimensions or int(os.environ.get("ADA_EMBEDDING_DIMENSIONS", "1536"))
        self.outputs = [
            OutputFieldMappingEntry(name="embedding", target_name="vector_output")
        ]
    
    def create_skill(self):
        if not self.resource_uri:
            raise ValueError("Azure OpenAI resource URI is required")
        
        return AzureOpenAIEmbeddingSkill(
            resource_uri=self.resource_uri,
            deployment_id=self.deployment_id,
            inputs=self.inputs,
            outputs=self.outputs
        )
