"""Azure AI Search client for creating indexes and querying documents."""

import logging
from typing import Dict, List
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex, SearchField, SearchFieldDataType,
    SimpleField, SearchableField
)

logger = logging.getLogger(__name__)


class AzureSearchClient:
    """Client for Azure AI Search operations."""
    
    def __init__(self, endpoint: str, api_key: str):
        if not endpoint or not api_key:
            raise ValueError("Endpoint and API key are required")
        self.endpoint = endpoint.rstrip("/")
        self.credential = AzureKeyCredential(api_key)
        self.index_client = SearchIndexClient(self.endpoint, self.credential)
        logger.info(f"AzureSearchClient initialized with endpoint: {self.endpoint}")
    
    def create_skill_index(self, skill_name: str) -> str:
        """Create an index tailored for a specific skill's output."""
        index_name = f"skill-explorer-{skill_name.lower().replace('skill', '')}"
        fields = self._get_fields_for_skill(skill_name)
        
        try:
            index = SearchIndex(name=index_name, fields=fields)
            self.index_client.create_or_update_index(index)
            logger.info(f"Index '{index_name}' created with {len(fields)} fields")
            return index_name
        except Exception as e:
            logger.error(f"Failed to create index '{index_name}': {str(e)}")
            raise
    
    def upload_document(self, index_name: str, document: Dict) -> bool:
        """Upload a document to the index."""
        try:
            search_client = SearchClient(self.endpoint, index_name, self.credential)
            result = search_client.upload_documents([document])
            success = result[0].succeeded
            logger.info(f"Document upload to '{index_name}': {'successful' if success else 'failed'}")
            return success
        except Exception as e:
            logger.error(f"Failed to upload document to '{index_name}': {str(e)}")
            raise
    
    def query_index(self, index_name: str, query: str = "*", top: int = 10) -> List[Dict]:
        """Query documents from the index."""
        try:
            search_client = SearchClient(self.endpoint, index_name, self.credential)
            results = search_client.search(query, top=top)
            docs = [dict(doc) for doc in results]
            logger.info(f"Query on '{index_name}' returned {len(docs)} documents")
            return docs
        except Exception as e:
            logger.error(f"Failed to query index '{index_name}': {str(e)}")
            raise
    
    def delete_index(self, index_name: str) -> bool:
        """Delete an index."""
        try:
            self.index_client.delete_index(index_name)
            logger.info(f"Index '{index_name}' deleted successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to delete index '{index_name}': {str(e)}")
            raise
    
    def list_indexes(self) -> List[str]:
        """List all indexes."""
        try:
            indexes = [idx.name for idx in self.index_client.list_indexes()]
            logger.info(f"Found {len(indexes)} indexes")
            return indexes
        except Exception as e:
            logger.error(f"Failed to list indexes: {str(e)}")
            raise
    
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
            "EntityLinkingSkill": [
                SearchableField(name="linkedEntities", type=SearchFieldDataType.Collection(SearchFieldDataType.String)),
                SimpleField(name="matches", type=SearchFieldDataType.String),
            ],
            "SplitSkill": [
                SearchableField(name="textItems", type=SearchFieldDataType.Collection(SearchFieldDataType.String)),
            ],
            "MergeSkill": [
                SearchableField(name="mergedText", type=SearchFieldDataType.String),
            ],
            "ShaperSkill": [
                SearchableField(name="shapedData", type=SearchFieldDataType.String),
            ],
            "ConditionalSkill": [
                SearchableField(name="condition", type=SearchFieldDataType.String),
                SearchableField(name="ifTrueOutput", type=SearchFieldDataType.String),
                SearchableField(name="ifFalseOutput", type=SearchFieldDataType.String),
            ],
            "OcrSkill": [
                SearchableField(name="text", type=SearchFieldDataType.String),
                SearchableField(name="layoutText", type=SearchFieldDataType.String),
            ],
            "ImageAnalysisSkill": [
                SearchableField(name="description", type=SearchFieldDataType.String),
                SearchableField(name="tags", type=SearchFieldDataType.Collection(SearchFieldDataType.String)),
                SearchableField(name="categories", type=SearchFieldDataType.Collection(SearchFieldDataType.String)),
            ],
            "VisionVectorizeSkill": [
                SimpleField(name="imageVector", type=SearchFieldDataType.Collection(SearchFieldDataType.Double)),
            ],
            "DocumentExtractionSkill": [
                SearchableField(name="extractedText", type=SearchFieldDataType.String),
                SimpleField(name="extractedMetadata", type=SearchFieldDataType.String),
            ],
            "DocumentIntelligenceLayoutSkill": [
                SearchableField(name="layoutContent", type=SearchFieldDataType.String),
                SimpleField(name="pageCount", type=SearchFieldDataType.Int32),
            ],
            "AzureOpenAIEmbeddingSkill": [
                SimpleField(name="embedding", type=SearchFieldDataType.Collection(SearchFieldDataType.Double)),
            ],
        }
        
        fields = base_fields + skill_fields.get(skill_name, [])
        logger.debug(f"Generated {len(fields)} fields for {skill_name}")
        return fields
    
    def prepare_document_for_index(self, skill_name: str, preview_doc: Dict) -> Dict:
        """Transform preview document to index-compatible format."""
        doc = {"id": preview_doc.get("id", "doc_001"), "content": preview_doc.get("content", "")}
        
        try:
            if skill_name == "LanguageDetectionSkill":
                doc["languageCode"] = preview_doc.get("languageCode", "")
                doc["languageName"] = preview_doc.get("languageName", "")
                doc["score"] = preview_doc.get("score", 0.0)
            
            elif skill_name == "KeyPhraseExtractionSkill":
                doc["keyPhrases"] = preview_doc.get("keyPhrases", [])
            
            elif skill_name == "EntityRecognitionSkill":
                doc["persons"] = preview_doc.get("persons", [])
                doc["locations"] = preview_doc.get("locations", [])
                doc["organizations"] = preview_doc.get("organizations", [])
            
            elif skill_name == "SentimentSkill":
                scores = preview_doc.get("confidenceScores", {})
                doc["sentiment"] = preview_doc.get("sentiment", "neutral")
                doc["positiveScore"] = scores.get("positive", 0)
                doc["neutralScore"] = scores.get("neutral", 0)
                doc["negativeScore"] = scores.get("negative", 0)
            
            elif skill_name == "PIIDetectionSkill":
                doc["maskedText"] = preview_doc.get("maskedText", "")
                doc["piiDetected"] = len(preview_doc.get("piiEntities", [])) > 0
            
            elif skill_name == "TextTranslationSkill":
                doc["translatedText"] = preview_doc.get("translatedText", "")
                doc["translatedToLanguageCode"] = preview_doc.get("translatedToLanguageCode", "")
            
            elif skill_name == "EntityLinkingSkill":
                doc["linkedEntities"] = preview_doc.get("linkedEntities", [])
                doc["matches"] = preview_doc.get("matches", "")
            
            elif skill_name == "SplitSkill":
                doc["textItems"] = preview_doc.get("textItems", [])
            
            elif skill_name == "MergeSkill":
                doc["mergedText"] = preview_doc.get("mergedText", "")
            
            elif skill_name == "ShaperSkill":
                doc["shapedData"] = preview_doc.get("shapedData", "")
            
            elif skill_name == "ConditionalSkill":
                doc["condition"] = preview_doc.get("condition", "")
                doc["ifTrueOutput"] = preview_doc.get("ifTrueOutput", "")
                doc["ifFalseOutput"] = preview_doc.get("ifFalseOutput", "")
            
            elif skill_name == "OcrSkill":
                doc["text"] = preview_doc.get("text", "")
                doc["layoutText"] = preview_doc.get("layoutText", "")
            
            elif skill_name == "ImageAnalysisSkill":
                doc["description"] = preview_doc.get("description", "")
                # Handle both list of strings and list of objects with 'name' property
                tags = preview_doc.get("tags", [])
                doc["tags"] = [t if isinstance(t, str) else t.get("name", "") for t in tags]
                doc["categories"] = preview_doc.get("categories", [])
            
            elif skill_name == "VisionVectorizeSkill":
                doc["imageVector"] = preview_doc.get("imageVector", [])
            
            elif skill_name == "DocumentExtractionSkill":
                doc["extractedText"] = preview_doc.get("extractedText", "")
                doc["extractedMetadata"] = preview_doc.get("extractedMetadata", "")
            
            elif skill_name == "DocumentIntelligenceLayoutSkill":
                doc["layoutContent"] = preview_doc.get("layoutContent", "")
                doc["pageCount"] = preview_doc.get("pageCount", 0)
            
            elif skill_name == "AzureOpenAIEmbeddingSkill":
                doc["embedding"] = preview_doc.get("embedding", [])
            
            else:
                # Generic fallback: copy all simple fields
                for key, value in preview_doc.items():
                    if key not in ("id", "content"):
                        if isinstance(value, (str, int, float, bool)):
                            doc[key] = value
                        elif isinstance(value, list) and value and isinstance(value[0], (str, int, float)):
                            doc[key] = value
            
            logger.debug(f"Prepared document for {skill_name} with {len(doc)} fields")
        except Exception as e:
            logger.error(f"Error preparing document for {skill_name}: {str(e)}")
            raise
        
        return doc
