"""Azure AI Search client for creating indexes and querying documents."""

from typing import Dict, List
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex, SearchField, SearchFieldDataType,
    SimpleField, SearchableField
)


class AzureSearchClient:
    """Client for Azure AI Search operations."""
    
    def __init__(self, endpoint: str, api_key: str):
        self.endpoint = endpoint.rstrip("/")
        self.credential = AzureKeyCredential(api_key)
        self.index_client = SearchIndexClient(self.endpoint, self.credential)
    
    def create_skill_index(self, skill_name: str) -> str:
        """Create an index tailored for a specific skill's output."""
        index_name = f"skill-explorer-{skill_name.lower().replace('skill', '')}"
        fields = self._get_fields_for_skill(skill_name)
        
        index = SearchIndex(name=index_name, fields=fields)
        self.index_client.create_or_update_index(index)
        return index_name
    
    def upload_document(self, index_name: str, document: Dict) -> bool:
        """Upload a document to the index."""
        search_client = SearchClient(self.endpoint, index_name, self.credential)
        result = search_client.upload_documents([document])
        return result[0].succeeded
    
    def query_index(self, index_name: str, query: str = "*", top: int = 10) -> List[Dict]:
        """Query documents from the index."""
        search_client = SearchClient(self.endpoint, index_name, self.credential)
        results = search_client.search(query, top=top)
        return [dict(doc) for doc in results]
    
    def delete_index(self, index_name: str) -> bool:
        """Delete an index."""
        self.index_client.delete_index(index_name)
        return True
    
    def list_indexes(self) -> List[str]:
        """List all indexes."""
        return [idx.name for idx in self.index_client.list_indexes()]
    
    def _get_fields_for_skill(self, skill_name: str) -> List[SearchField]:
        """Get index fields based on skill output schema."""
        base_fields = [
            SimpleField(name="id", type=SearchFieldDataType.String, key=True),
            SearchableField(name="content", type=SearchFieldDataType.String),
        ]
        
        skill_fields = {
            "LanguageDetectionSkill": [
                SimpleField(name="languageCode", type=SearchFieldDataType.String, filterable=True),
                SearchableField(name="languageName", type=SearchFieldDataType.String),
                SimpleField(name="score", type=SearchFieldDataType.Double),
            ],
            "KeyPhraseExtractionSkill": [
                SearchableField(name="keyPhrases", type=SearchFieldDataType.Collection(SearchFieldDataType.String)),
            ],
            "EntityRecognitionSkill": [
                SearchableField(name="persons", type=SearchFieldDataType.Collection(SearchFieldDataType.String), filterable=True),
                SearchableField(name="locations", type=SearchFieldDataType.Collection(SearchFieldDataType.String), filterable=True),
                SearchableField(name="organizations", type=SearchFieldDataType.Collection(SearchFieldDataType.String), filterable=True),
            ],
            "SentimentSkill": [
                SimpleField(name="sentiment", type=SearchFieldDataType.String, filterable=True, facetable=True),
                SimpleField(name="positiveScore", type=SearchFieldDataType.Double),
                SimpleField(name="neutralScore", type=SearchFieldDataType.Double),
                SimpleField(name="negativeScore", type=SearchFieldDataType.Double),
            ],
            "PIIDetectionSkill": [
                SearchableField(name="maskedText", type=SearchFieldDataType.String),
                SimpleField(name="piiDetected", type=SearchFieldDataType.Boolean, filterable=True),
            ],
            "TextTranslationSkill": [
                SearchableField(name="translatedText", type=SearchFieldDataType.String),
                SimpleField(name="translatedToLanguageCode", type=SearchFieldDataType.String, filterable=True),
            ],
            "OcrSkill": [
                SearchableField(name="text", type=SearchFieldDataType.String),
                SearchableField(name="layoutText", type=SearchFieldDataType.String),
            ],
            "ImageAnalysisSkill": [
                SearchableField(name="imageDescription", type=SearchFieldDataType.String),
                SearchableField(name="imageTags", type=SearchFieldDataType.Collection(SearchFieldDataType.String)),
            ],
            "SplitSkill": [
                SearchableField(name="textItems", type=SearchFieldDataType.Collection(SearchFieldDataType.String)),
            ],
            "MergeSkill": [
                SearchableField(name="mergedText", type=SearchFieldDataType.String),
            ],
        }
        
        return base_fields + skill_fields.get(skill_name, [])
    
    def prepare_document_for_index(self, skill_name: str, preview_doc: Dict) -> Dict:
        """Transform preview document to index-compatible format."""
        doc = {"id": preview_doc.get("id", "doc_001"), "content": preview_doc.get("content", "")}
        
        if skill_name == "SentimentSkill":
            scores = preview_doc.get("confidenceScores", {})
            doc["sentiment"] = preview_doc.get("sentiment", "neutral")
            doc["positiveScore"] = scores.get("positive", 0)
            doc["neutralScore"] = scores.get("neutral", 0)
            doc["negativeScore"] = scores.get("negative", 0)
        elif skill_name == "PIIDetectionSkill":
            doc["maskedText"] = preview_doc.get("maskedText", "")
            doc["piiDetected"] = len(preview_doc.get("piiEntities", [])) > 0
        elif skill_name == "ImageAnalysisSkill":
            desc = preview_doc.get("description", {})
            captions = desc.get("captions", [])
            doc["imageDescription"] = captions[0].get("text", "") if captions else ""
            doc["imageTags"] = [t.get("name", "") for t in preview_doc.get("tags", [])]
        else:
            # Copy simple fields directly
            for key, value in preview_doc.items():
                if key not in ("id", "content") and not isinstance(value, (dict, list)) or isinstance(value, list) and value and isinstance(value[0], str):
                    doc[key] = value
        
        return doc
