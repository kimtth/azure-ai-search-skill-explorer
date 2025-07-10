import os
import time
import json
from typing import List, Dict, Union
from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexClient, SearchIndexerClient
from azure.search.documents.indexes.models import (
    SearchIndexer, SearchIndexerDataSourceConnection, SearchIndexerSkillset,
    SearchField, SearchFieldDataType, IndexingParameters,
    SearchIndex, FieldMapping, OutputFieldMappingEntry,
    CognitiveServicesAccountKey, VectorSearch, HnswAlgorithmConfiguration,
    VectorSearchProfile
)
from azure.search.documents import SearchClient

# Import all skill test classes
from skill import (
    LanguageDetectionSkillTest, KeyPhraseExtractionSkillTest,
    EntityRecognitionSkillTest, SentimentSkillTest, PIIDetectionSkillTest,
    TextTranslationSkillTest, EntityLinkingSkillTest, CustomEntityLookupSkillTest,
    VisionVectorizeSkillTest, OcrSkillTest, ImageAnalysisSkillTest,
    DocumentExtractionSkillTest, DocumentIntelligenceLayoutSkillTest,
    ConditionalSkillTest, MergeSkillTest, ShaperSkillTest, SplitSkillTest,
    AzureOpenAIEmbeddingSkillTest
)

from .blob_control import BlobController
from .ai_search_control import AiSearchController

# Load environment variables
load_dotenv()

class AzureSearchSkillTester:
    def __init__(self):
        # Azure Search configuration
        self.service_name = os.environ.get("SEARCH_SERVICE_NAME", "")
        self.admin_key = os.environ.get("SEARCH_ADMIN_KEY", "")
        self.query_key = os.environ.get("SEARCH_QUERY_KEY", "")
        self.cognitive_services_key = os.environ.get("COGNITIVE_SERVICES_KEY", "")
        
        # Storage configuration
        self.storage_account_name = os.environ.get("STORAGE_ACCOUNT_NAME", "")
        self.storage_account_key = os.environ.get("STORAGE_ACCOUNT_KEY", "")
        # where test blobs live
        self.test_container_name = "aisearch-skill-test-data"

        # init blob storage
        self.blob_controller = BlobController(
            self.storage_account_name,
            self.storage_account_key,
            self.test_container_name
        )
        # init AI Search controller
        self.ai_search = AiSearchController(
            self.service_name,
            self.admin_key,
            self.query_key
        )

        # Azure OpenAI configuration
        self.aoai_resource_uri = os.environ.get("AOAI_RESOURCE_URI", "")
        self.aoai_deployment_id = os.environ.get("AOAI_DEPLOYMENT_ID", "")
        self.embedding_dimensions = int(os.environ.get("ADA_EMBEDDING_DIMENSIONS", "10"))
        
        # Initialize clients
        self.search_service_endpoint = f"https://{self.service_name}.search.windows.net/"
        # ensure keys are strings
        self.admin_key = str(self.admin_key)
        self.query_key = str(self.query_key)
        self.admin_credential = AzureKeyCredential(self.admin_key)
        self.query_credential = AzureKeyCredential(self.query_key)
        self.index_client = SearchIndexClient(self.search_service_endpoint, self.admin_credential)
        self.indexer_client = SearchIndexerClient(self.search_service_endpoint, self.admin_credential)
        
        # Test container
        self.test_container_name = "aisearch-skill-test-data"
        
        # Initialize parsers
        from parse.markitdown_parser import MarkitdownParser
        self.parser = MarkitdownParser()
        
    def _create_test_resources(self, skill_name: str, unique_id: str) -> Dict[str, str]:
        """Create unique resource names for testing."""
        return {
            "ds_name": f"ds-{skill_name}-{unique_id}",
            "skillset_name": f"ss-{skill_name}-{unique_id}",
            "index_name": f"idx-{skill_name}-{unique_id}",
            "indexer_name": f"ixr-{skill_name}-{unique_id}"
        }
    
    def _create_data_source(self, ds_name: str) -> None:
        """Create Azure AI Search data source."""
        ds = self.indexer_client.get_data_source_connection(ds_name)
        if ds:
            print(f"Data source {ds_name} already exists. Skipping creation.")
            return

        data_source_connection = SearchIndexerDataSourceConnection(
            name=ds_name,
            type="azureblob",
            connection_string=self.blob_controller.get_connection_string(),
            container={"name": self.test_container_name}
        )
        self.index_client.create_or_update_data_source_connection(data_source_connection)
    
    def _create_skillset(self, skillset_name: str, skills: list) -> None:
        sks = self.indexer_client.get_skillset(skillset_name)
        if sks:
            print(f"Skillset {skillset_name} already exists. Skipping creation.")
            return

        """Create Azure AI Search skillset."""
        skillset = SearchIndexerSkillset(
            name=skillset_name,
            description="Skillset for testing",
            skills=skills,
            cognitive_services_account=CognitiveServicesAccountKey(key=self.cognitive_services_key)
        )
        self.index_client.create_or_update_skillset(skillset)
    
    def _create_index(self, index_name: str, has_vector: bool = False, vector_dims: int = None) -> None:
        """Create search index with appropriate fields."""
        index = self.index_client.get_index(index_name)
        if index:
            print(f"Index {index_name} already exists. Skipping creation.")
            return

        fields = [
            SearchField(name="id", type=SearchFieldDataType.String, key=True),
            SearchField(name="content", type=SearchFieldDataType.String, searchable=True),
            SearchField(name="content_output", type=SearchFieldDataType.String, searchable=True),
            SearchField(name="collection_output", type=SearchFieldDataType.Collection(SearchFieldDataType.String), searchable=True),
        ]
        
        vector_search = None
        if has_vector and vector_dims:
            fields.append(
                SearchField(
                    name="vector_output",
                    type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                    searchable=True,
                    vector_search_dimensions=vector_dims,
                    vector_search_profile_name="my-vector-profile"
                )
            )
            vector_search = VectorSearch(
                profiles=[VectorSearchProfile(name="my-vector-profile", algorithm_configuration_name="my-hnsw")],
                algorithms=[HnswAlgorithmConfiguration(name="my-hnsw")]
            )
        
        index = SearchIndex(
            name=index_name,
            fields=fields,
            vector_search=vector_search
        )
        self.index_client.create_or_update_index(index)
    
    def _create_and_run_indexer(self, indexer_name: str, ds_name: str, skillset_name: str, 
                               index_name: str, output_mappings: list, needs_images: bool = False) -> None:
        """Create and run indexer."""
        indexer = self.indexer_client.get_indexer(indexer_name)
        if indexer:
            print(f"Indexer {indexer_name} already exists. Skipping creation.")
            return

        field_mappings = [
            FieldMapping(
                source_field_name="metadata_storage_path",
                target_field_name="id",
                mapping_function={"name": "base64Encode"}
            ),
            FieldMapping(source_field_name="content", target_field_name="content")
        ]
        
        parameters = IndexingParameters(
            batch_size=1,
            max_failed_items=-1,
            max_failed_items_per_batch=-1
        )
        
        if needs_images:
            parameters.configuration = {
                "dataToExtract": "contentAndMetadata",
                "imageAction": "generateNormalizedImages"
            }
        
        indexer = SearchIndexer(
            name=indexer_name,
            data_source_name=ds_name,
            skillset_name=skillset_name,
            target_index_name=index_name,
            field_mappings=field_mappings,
            output_field_mappings=output_mappings,
            parameters=parameters
        )
        
        self.index_client.create_or_update_indexer(indexer)
        self.index_client.run_indexer(indexer_name)
        
        # Wait for completion
        self._wait_for_indexer(indexer_name)
    
    def _wait_for_indexer(self, indexer_name: str, timeout: int = 60) -> None:
        """Wait for indexer to complete."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            status = self.index_client.get_indexer_status(indexer_name)
            if status.last_result and status.last_result.status in ["success", "transientFailure", "error"]:
                if status.last_result.errors:
                    print(f"Indexer errors: {status.last_result.errors}")
                break
            time.sleep(2)
    
    def _fetch_results(self, index_name: str) -> List[Dict]:
        """Fetch results from index."""
        search_client = SearchClient(self.search_service_endpoint, index_name, self.query_credential)
        results = []
        
        for result in search_client.search(search_text="*", include_total_count=True):
            doc = {k: v for k, v in result.items() if not k.startswith('@')}
            results.append(doc)
        
        return results
    
    def _cleanup_resources(self, resources: Dict[str, str]) -> None:
        """Clean up test resources."""
        for resource_type, name in [
            ("indexer", resources["indexer_name"]),
            ("index", resources["index_name"]),
            ("skillset", resources["skillset_name"]),
            ("data_source", resources["ds_name"])
        ]:
            try:
                if resource_type == "indexer":
                    self.index_client.delete_indexer(name)
                elif resource_type == "index":
                    self.index_client.delete_index(name)
                elif resource_type == "skillset":
                    self.index_client.delete_skillset(name)
                elif resource_type == "data_source":
                    self.index_client.delete_data_source_connection(name)
            except Exception as e:
                print(f"Error deleting {resource_type} {name}: {e}")
    
    def test_skill(self, skill, test_input: Union[str, bytes], skill_name: str,
                   is_image: bool = False, has_vector_output: bool = False, 
                   vector_dims: int = None) -> List[Dict]:
        """Generic method to test any skill."""
        unique_id = str(int(time.time() * 1000))
        resources = self._create_test_resources(skill_name.lower(), unique_id)
        
        try:
            # Upload test data
            print(f"\nTesting {skill_name}...")
            self.blob_controller.upload_test_data(test_input, unique_id, is_image)
            
            # Create resources
            self.ai_search.create_data_source(
                resources["ds_name"],
                self.blob_controller.get_connection_string(),
                self.test_container_name
            )
            self.ai_search.create_skillset(
                resources["skillset_name"],
                [skill],
                self.cognitive_services_key
            )
            self.ai_search.create_index(
                resources["index_name"],
                has_vector_output,
                vector_dims
            )

            # Determine output mappings
            output_mappings = []
            for output in skill.outputs:
                target_field = "vector_output" if has_vector_output else \
                             "collection_output" if any(x in output.name.lower() for x in ["phrases", "entities", "tags"]) else \
                             "content_output"
                output_mappings.append(
                    OutputFieldMappingEntry(
                        source_field_name=f"/document/{output.target_name}",
                        target_field_name=target_field
                    )
                )
            
            # Create and run indexer
            self.ai_search.create_and_run_indexer(
                resources["indexer_name"],
                resources["ds_name"],
                resources["skillset_name"],
                resources["index_name"],
                output_mappings,
                is_image
            )
            
            # Fetch and return results
            results = self.ai_search.fetch_results(resources["index_name"])
            if results:
                print(f"Results for {skill_name}:")
                for result in results:
                    print(json.dumps(result, indent=2))
            return results
            
        finally:
            self.ai_search.cleanup_resources(resources)
    
    def process_file_input(self, file_path: str) -> Union[str, bytes, None]:
        """Process file input and return appropriate content for skills."""
        if not file_path or not os.path.exists(file_path):
            return None
            
        # Check if it's an image file
        image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff'}
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext in image_extensions:
            # Return raw bytes for image files
            try:
                with open(file_path, 'rb') as f:
                    return f.read()
            except Exception as e:
                print(f"Error reading image file: {e}")
                return None
        else:
            # Use parser for text-based files
            try:
                result = self.parser.parse_by_filepath(file_path)
                if result['success']:
                    return result['text_content']
                else:
                    print(f"Failed to parse file: {result['error']}")
                    return None
            except Exception as e:
                print(f"Error parsing file: {e}")
                return None
    
    def test_skill_with_class(self, skill_test_class, custom_input=None, file_path=None) -> List[Dict]:
        """Test a skill using the OOP approach with optional file input."""
        try:
            # Handle special case for embedding skill
            if skill_test_class == AzureOpenAIEmbeddingSkillTest:
                skill_test = skill_test_class(
                    self.aoai_resource_uri,
                    self.aoai_deployment_id,
                    self.embedding_dimensions
                )
            else:
                skill_test = skill_test_class()
            
            skill = skill_test.create_skill()
            
            # Determine test input priority: custom_input > file_path > sample_input
            if custom_input:
                test_input = custom_input
            elif file_path:
                test_input = self.process_file_input(file_path)
                if test_input is None:
                    print(f"Failed to process file: {file_path}")
                    return []
            else:
                test_input = skill_test.get_sample_input()
            
            return self.test_skill(
                skill,
                test_input,
                skill_test.skill_name,
                is_image=skill_test.requires_image_processing,
                has_vector_output=skill_test.has_vector_output,
                vector_dims=skill_test.vector_dimensions
            )
        except Exception as e:
            print(f"Error creating skill test for {skill_test_class.__name__}: {e}")
            return []

    def test_all_skills(self):
        """Test all built-in skills using OOP approach."""
        # Text skills
        text_skills = [
            LanguageDetectionSkillTest,
            KeyPhraseExtractionSkillTest,
            EntityRecognitionSkillTest,
            SentimentSkillTest,
            PIIDetectionSkillTest,
            TextTranslationSkillTest,
            EntityLinkingSkillTest,
            CustomEntityLookupSkillTest,
            VisionVectorizeSkillTest,
        ]
        
        # Image skills
        image_skills = [
            OcrSkillTest,
            ImageAnalysisSkillTest,
        ]
        
        # Document skills
        document_skills = [
            DocumentExtractionSkillTest,
            DocumentIntelligenceLayoutSkillTest,
        ]
        
        # Utility skills
        utility_skills = [
            ConditionalSkillTest,
            MergeSkillTest,
            ShaperSkillTest,
            SplitSkillTest,
        ]
        
        print("\n=== Testing Text Skills ===")
        for skill_class in text_skills:
            try:
                results = self.test_skill_with_class(skill_class)
                skill_test = skill_class()
                print(skill_test.format_results(results))
            except Exception as e:
                print(f"Error testing {skill_class.__name__}: {e}")
        
        print("\n=== Testing Image Skills ===")
        for skill_class in image_skills:
            try:
                results = self.test_skill_with_class(skill_class)
                skill_test = skill_class()
                print(skill_test.format_results(results))
            except Exception as e:
                print(f"Error testing {skill_class.__name__}: {e}")
        
        print("\n=== Testing Document Skills ===")
        for skill_class in document_skills:
            try:
                results = self.test_skill_with_class(skill_class)
                skill_test = skill_class()
                print(skill_test.format_results(results))
            except Exception as e:
                print(f"Error testing {skill_class.__name__}: {e}")
        
        print("\n=== Testing Utility Skills ===")
        for skill_class in utility_skills:
            try:
                results = self.test_skill_with_class(skill_class)
                skill_test = skill_class()
                print(skill_test.format_results(results))
            except Exception as e:
                print(f"Error testing {skill_class.__name__}: {e}")
        
        # Test embedding skill if configured
        if self.aoai_resource_uri and self.aoai_resource_uri != "YOUR_AOAI_RESOURCE_URI":
            print("\n=== Testing Embedding Skill ===")
            self._test_embedding_skill()

    def _test_embedding_skill(self):
        """Test Azure OpenAI Embedding skill."""
        from skill.embedding_skills import AzureOpenAIEmbeddingSkillTest
        
        try:
            skill_test = AzureOpenAIEmbeddingSkillTest(
                self.aoai_resource_uri,
                self.aoai_deployment_id,
                self.embedding_dimensions
            )
            results = self.test_skill_with_class(skill_test)
            print(skill_test.format_results(results))
        except Exception as e:
            print(f"Error testing embedding skill: {e}")

