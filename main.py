import os
import time
import base64
from typing import Optional, List, Dict, Union

from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndexer, SearchIndexerDataSourceConnection, SearchIndexerSkillset,
    SearchIndexerTargetIndex, SearchIndexerDataContainer,
    SearchField, SearchFieldDataType,
    OcrSkill, LanguageDetectionSkill, KeyPhraseExtractionSkill,
    CognitiveServicesAccountKey, IndexingParameters, Skill,
    VectorSearch, HnswAlgorithmConfiguration, VectorSearchProfile,
    SentimentSkill, EntityRecognitionSkill, AzureOpenAIEmbeddingSkill,
    ImageAnalysisSkill, PIIDetectionSkill, TextTranslationSkill,
    SplitSkill, MergeSkill # Included for completeness, but typically require chaining
)
from azure.search.documents import SearchClient
from azure.storage.blob import BlobServiceClient
from PIL import Image, ImageDraw, ImageFont # For creating dummy images for OCR test
from io import BytesIO

# --- Configuration ---
# Replace with your actual service details
# It's highly recommended to use environment variables for sensitive information
SERVICE_NAME = os.environ.get("SEARCH_SERVICE_NAME", "YOUR_SEARCH_SERVICE_NAME")
ADMIN_KEY = os.environ.get("SEARCH_ADMIN_KEY", "YOUR_SEARCH_ADMIN_KEY")
QUERY_KEY = os.environ.get("SEARCH_QUERY_KEY", "YOUR_SEARCH_QUERY_KEY")
COGNITIVE_SERVICES_KEY = os.environ.get("COGNITIVE_SERVICES_KEY", "YOUR_COGNITIVE_SERVICES_KEY") # For general AI Services
STORAGE_ACCOUNT_NAME = os.environ.get("STORAGE_ACCOUNT_NAME", "YOUR_STORAGE_ACCOUNT_NAME")
STORAGE_ACCOUNT_KEY = os.environ.get("STORAGE_ACCOUNT_KEY", "YOUR_STORAGE_ACCOUNT_KEY")
# Azure OpenAI details for embedding skill (if used)
AOAI_RESOURCE_URI = os.environ.get("AOAI_RESOURCE_URI", "YOUR_AOAI_RESOURCE_URI")
AOAI_DEPLOYMENT_ID = os.environ.get("AOAI_DEPLOYMENT_ID", "text-embedding-ada-002") # e.g., "text-embedding-ada-002"
ADA_EMBEDDING_DIMENSIONS = int(os.environ.get("ADA_EMBEDDING_DIMENSIONS", "1536")) # Dimensions for Ada embeddings

TEST_CONTAINER_NAME = "aisearch-skill-test-data" # This blob container will be created/used for test data

# --- Clients ---
search_service_endpoint = f"https://{SERVICE_NAME}.search.windows.net/"
admin_credential = AzureKeyCredential(ADMIN_KEY)
query_credential = AzureKeyCredential(QUERY_KEY)
index_client = SearchIndexClient(search_service_endpoint, admin_credential)

# --- Helper Functions (Re-used from previous response) ---

def create_blob_connection_string(account_name, account_key):
    """Constructs the Azure Blob Storage connection string."""
    return f"DefaultEndpointsProtocol=https;AccountName={account_name};AccountKey={account_key};EndpointSuffix=core.windows.net"

def create_data_source(ds_name: str, container_name: str):
    """Creates or updates an Azure AI Search data source."""
    print(f"Creating data source: {ds_name}")
    data_source_connection = SearchIndexerDataSourceConnection(
        name=ds_name,
        type="azureblob",
        credentials={"connectionString": create_blob_connection_string(STORAGE_ACCOUNT_NAME, STORAGE_ACCOUNT_KEY)},
        container=SearchIndexerDataContainer(name=container_name)
    )
    index_client.create_or_update_data_source_connection(data_source_connection)

def create_skillset(skillset_name: str, skills: list[Skill], cognitive_services_key: str):
    """Creates or updates an Azure AI Search skillset."""
    print(f"Creating skillset: {skillset_name}")
    skillset = SearchIndexerSkillset(
        name=skillset_name,
        description="Skillset for individual skill testing",
        skills=skills,
        cognitive_services_account=CognitiveServicesAccountKey(key=cognitive_services_key)
    )
    index_client.create_or_or_update_skillset(skillset)

def create_and_run_indexer(indexer_name: str, ds_name: str, skillset_name: str, index_name: str, output_field_mappings: list, image_processing_enabled: bool = False):
    """Creates and runs an Azure AI Search indexer, then waits for its completion."""
    print(f"Creating indexer: {indexer_name}")

    # Default field mappings: map blob path to 'id' and blob content to 'content'
    field_mappings = [
        {"source_field_name": "metadata_storage_path", "target_field_name": "id", "mapping_function": {"name": "base64Encode"}},
        {"source_field_name": "content", "target_field_name": "content"}
    ]

    indexer_params = {
        "batch_size": 1, # Process one document at a time for focused testing
        "max_failed_items": -1, # Allow failures for testing purposes
        "max_failed_items_per_batch": -1
    }

    if image_processing_enabled:
        # Configuration for image processing if OCR or Image Analysis skills are used
        indexer_params["configuration"] = {"dataToExtract": "contentAndMetadata", "imageAction": "generateNormalizedImages"}

    indexer = SearchIndexer(
        name=indexer_name,
        data_source_name=ds_name,
        skillset_name=skillset_name,
        target_index_name=index_name,
        field_mappings=field_mappings,
        output_field_mappings=output_field_mappings,
        parameters=IndexingParameters(**indexer_params)
    )
    index_client.create_or_update_indexer(indexer)

    print(f"Running indexer: {indexer_name}...")
    index_client.run_indexer(indexer_name)

    # Simple polling to wait for indexer to complete
    while True:
        status = index_client.get_indexer_status(indexer_name)
        if status.last_result and status.last_result.status in ["success", "transientFailure", "error"]:
            print(f"Indexer status: {status.last_result.status}")
            if status.last_result.error_message:
                print(f"Indexer Error: {status.last_result.error_message}")
            break
        print(f"Indexer still running... Current status: {status.last_result.status if status.last_result else 'No runs yet'}")
        time.sleep(3) # Wait for 3 seconds before checking again

def clean_up_resources(ds_name: str, skillset_name: str, index_name: str, indexer_name: str):
    """Deletes all temporary Azure AI Search resources."""
    print("\nCleaning up resources...")
    try:
        index_client.delete_indexer(indexer_name)
        print(f"Deleted indexer: {indexer_name}")
    except Exception as e:
        print(f"Error deleting indexer {indexer_name}: {e}")
    try:
        index_client.delete_index(index_name)
        print(f"Deleted index: {index_name}")
    except Exception as e:
        print(f"Error deleting index {index_name}: {e}")
    try:
        index_client.delete_skillset(skillset_name)
        print(f"Deleted skillset: {skillset_name}")
    except Exception as e:
        print(f"Error deleting skillset {skillset_name}: {e}")
    try:
        index_client.delete_data_source_connection(ds_name)
        print(f"Deleted data source: {ds_name}")
    except Exception as e:
        print(f"Error deleting data source {ds_name}: {e}")

def fetch_indexed_data(index_name: str, select_fields: Optional[List[str]] = None) -> List[Dict]:
    """
    Fetches documents from the specified index and returns them as a list of dictionaries.
    """
    print(f"Fetching data from index: {index_name}...")
    search_client = SearchClient(search_service_endpoint, index_name, query_credential)
    
    results = []
    search_results = search_client.search(search_text="*", select=",".join(select_fields) if select_fields else None)
    
    for result in search_results:
        doc = {}
        for field_name in result.keys():
            if not field_name.startswith('@odata'):
                doc[field_name] = result.get(field_name)
        results.append(doc)
    
    print(f"Fetched {len(results)} documents.")
    return results

def test_single_skill(
    skill_to_test: Skill,
    input_text: Optional[str] = None,
    input_image_bytes: Optional[bytes] = None,
    test_id: str = "testdoc1",
    vector_dimensions: Optional[int] = None # Required if the skill outputs a vector
) -> List[Dict]:
    """
    Generic function to test a single built-in Azure AI Search skill with simplified index mapping.
    Outputs are mapped to 'content_string_output', 'content_string_collection_output', or 'vector_output'
    based on the skill's expected output type.
    """
    # Generate unique names for resources to avoid conflicts
    unique_suffix = str(time.time_ns())
    ds_name = f"ds-{skill_to_test.__class__.__name__.lower()}-{unique_suffix}"
    skillset_name = f"ss-{skill_to_test.__class__.__name__.lower()}-{unique_suffix}"
    index_name = f"idx-{skill_to_test.__class__.__name__.lower()}-{unique_suffix}"
    indexer_name = f"ixr-{skill_to_test.__class__.__name__.lower()}-{unique_suffix}"

    try:
        # Step 0: Upload test data to a unique folder in Azure Blob Storage
        blob_service_client = BlobServiceClient.from_connection_string(
            create_blob_connection_string(STORAGE_ACCOUNT_NAME, STORAGE_ACCOUNT_KEY)
        )
        container_client = blob_service_client.get_container_client(TEST_CONTAINER_NAME)
        
        try:
            container_client.create_container()
            print(f"Created blob container: {TEST_CONTAINER_NAME}")
        except Exception as e:
            if "ContainerAlreadyExists" in str(e):
                print(f"Blob container '{TEST_CONTAINER_NAME}' already exists.")
            else:
                raise e

        blob_path = f"test_data/{test_id}/input.txt" # Default for text input
        if input_image_bytes:
            blob_path = f"test_data/{test_id}/input.jpg" # For image inputs
            blob_client = container_client.get_blob_client(blob_path)
            blob_client.upload_blob(input_image_bytes, overwrite=True)
            print(f"Uploaded test image to blob: {blob_path}")
        elif input_text:
            blob_client = container_client.get_blob_client(blob_path)
            blob_client.upload_blob(input_text.encode('utf-8'), overwrite=True)
            print(f"Uploaded test text to blob: {blob_path}")
        else:
            raise ValueError("Either input_text or input_image_bytes must be provided.")

        # Step 1: Create Data Source
        create_data_source(ds_name, TEST_CONTAINER_NAME)

        # Step 2: Define Skillset
        requires_image_processing = False
        for skill_input in skill_to_test.inputs:
            if skill_input.name == "text" and input_text is not None:
                skill_input.source = "/document/content"
            elif skill_input.name == "image" and input_image_bytes is not None:
                skill_input.source = "/document/normalized_images/*"
                requires_image_processing = True

        create_skillset(skillset_name, [skill_to_test], COGNITIVE_SERVICES_KEY)

        # Step 3: Create Index with generic output fields
        index_fields = [
            SearchField(name="id", type=SearchFieldDataType.STRING, key=True, filterable=True, retrievable=True),
            SearchField(name="content", type=SearchFieldDataType.STRING, searchable=True, retrievable=True),
            SearchField(name="content_string_output", type=SearchFieldDataType.STRING, searchable=True, retrievable=True),
            SearchField(name="content_string_collection_output", type=SearchFieldDataType.COLLECTION_STRING, searchable=True, retrievable=True)
        ]
        
        vector_search_config = None
        output_field_name_in_index = None

        if skill_to_test.outputs:
            first_output_target_name = skill_to_test.outputs[0].target_name.lower()
            
            if "vector" in first_output_target_name or "embedding" in first_output_target_name:
                if vector_dimensions is None:
                    raise ValueError(f"Skill '{skill_to_test.__class__.__name__}' outputs a vector. 'vector_dimensions' must be provided.")
                
                index_fields.append(
                    SearchField(
                        name="vector_output",
                        type=SearchFieldDataType.COLLECTION_SINGLE,
                        searchable=True,
                        retrievable=True,
                        dimensions=vector_dimensions,
                        vector_search_profile="my-vector-profile"
                    )
                )
                vector_search_config = VectorSearch(
                    profiles=[VectorSearchProfile(name="my-vector-profile", algorithm="my-hnnsw-algorithm")],
                    algorithms=[HnswAlgorithmConfiguration(name="my-hnnsw-algorithm")]
                )
                output_field_name_in_index = "vector_output"

            elif any(t in first_output_target_name for t in ["keyphrases", "entities", "sentences", "tags", "phrases"]):
                output_field_name_in_index = "content_string_collection_output"
            else:
                output_field_name_in_index = "content_string_output"
        else:
            output_field_name_in_index = "content"


        index_definition = {
            "name": index_name,
            "fields": index_fields
        }
        if vector_search_config:
            index_definition["vectorSearch"] = vector_search_config

        print(f"Creating index: {index_name} with fields: {[f.name for f in index_fields]}")
        index_client.create_or_update_index(index_definition)

        # Step 4: Create and Run Indexer
        output_mappings = []
        if output_field_name_in_index:
            for output in skill_to_test.outputs:
                output_mappings.append({
                    "sourceFieldName": f"/document/{output.target_name}",
                    "targetFieldName": output_field_name_in_index
                })
        
        output_mappings.append({"sourceFieldName": "/document/content", "targetFieldName": "content"})

        create_and_run_indexer(indexer_name, ds_name, skillset_name, index_name, output_mappings, requires_image_processing)

        # Step 5: Fetch results
        select_fields = ["id", "content", "content_string_output", "content_string_collection_output"]
        if output_field_name_in_index == "vector_output":
            select_fields.append("vector_output")

        indexed_documents = fetch_indexed_data(index_name, select_fields=select_fields)

        if indexed_documents:
            print(f"\n--- Test Results for {skill_to_test.__class__.__name__} ---")
            for doc in indexed_documents:
                print(f"Document ID: {doc.get('id')}")
                print(f"Original Content: {doc.get('content')[:100]}...") # Truncate for display
                print(f"Skill Output ({output_field_name_in_index}): {doc.get(output_field_name_in_index)}")
            return indexed_documents
        else:
            print("No documents found in the index after enrichment.")
            return []

    finally:
        # Step 6: Clean up resources
        clean_up_resources(ds_name, skillset_name, index_name, indexer_name)


# --- Example Usage for various skills ---

if __name__ == "__main__":
    # --- IMPORTANT: Set your environment variables before running ---
    # Example (replace with your actual values):
    # os.environ["SEARCH_SERVICE_NAME"] = "your-search-service-name"
    # os.environ["SEARCH_ADMIN_KEY"] = "your-admin-key"
    # os.environ["SEARCH_QUERY_KEY"] = "your-query-key"
    # os.environ["COGNITIVE_SERVICES_KEY"] = "your-cognitive-services-key" # For general AI Services
    # os.environ["STORAGE_ACCOUNT_NAME"] = "yourstorageaccountname"
    # os.environ["STORAGE_ACCOUNT_KEY"] = "yourstorageaccountkey"
    # os.environ["AOAI_RESOURCE_URI"] = "https://your-aoai-resource.openai.azure.com"
    # os.environ["AOAI_DEPLOYMENT_ID"] = "text-embedding-ada-002"
    # os.environ["ADA_EMBEDDING_DIMENSIONS"] = "1536"

    if "YOUR_SEARCH_SERVICE_NAME" in SERVICE_NAME:
        print("Please set your Azure AI Search service details, Cognitive Services key, and Storage details in environment variables or directly in the script.")
        print("Example: SEARCH_SERVICE_NAME, SEARCH_ADMIN_KEY, SEARCH_QUERY_KEY, COGNITIVE_SERVICES_KEY, STORAGE_ACCOUNT_NAME, STORAGE_ACCOUNT_KEY, AOAI_RESOURCE_URI, AOAI_DEPLOYMENT_ID, ADA_EMBEDDING_DIMENSIONS")
        exit(1)

    # --- Test LanguageDetectionSkill (String Output) ---
    print("\n--- Testing LanguageDetectionSkill ---")
    lang_detect_skill = LanguageDetectionSkill(
        inputs=[{"name": "text", "source": "/document/content"}],
        outputs=[{"name": "languageCode", "target_name": "detectedLanguage"}]
    )
    test_single_skill(
        lang_detect_skill,
        input_text="Hello, this is a test in English. This sentence is in Japanese: こんにちは。",
        test_id="lang_test_doc"
    )

    # --- Test KeyPhraseExtractionSkill (Collection(String) Output) ---
    print("\n--- Testing KeyPhraseExtractionSkill ---")
    keyphrase_skill = KeyPhraseExtractionSkill(
        inputs=[
            {"name": "text", "source": "/document/content"},
            {"name": "languageCode", "source": "/document/detectedLanguage"} # Assumes language detection or default
        ],
        outputs=[{"name": "keyPhrases", "target_name": "extractedKeyPhrases"}]
    )
    test_single_skill(
        keyphrase_skill,
        input_text="Azure AI Search is a powerful search-as-a-service solution. It provides full-text search, vector search, and hybrid capabilities.",
        test_id="keyphrase_test_doc"
    )

    # --- Test OcrSkill (String Output, requires image) ---
    print("\n--- Testing OcrSkill ---")
    try:
        img = Image.new('RGB', (300, 150), color = 'white')
        d = ImageDraw.Draw(img)
        try:
            fnt = ImageFont.truetype("arial.ttf", 40)
        except IOError:
            print("Warning: Arial font not found, using default. OCR text quality might be affected.")
            fnt = ImageFont.load_default()
        d.text((20, 50), "OCR TEST TEXT", fill=(0,0,0), font=fnt)
        img_byte_arr = BytesIO()
        img.save(img_byte_arr, format='PNG')
        image_bytes_with_text = img_byte_arr.getvalue()

        ocr_skill = OcrSkill(
            inputs=[{"name": "image", "source": "/document/normalized_images/*"}],
            outputs=[{"name": "text", "target_name": "ocrExtractedText"}],
            line_ending="Layout"
        )
        test_single_skill(
            ocr_skill,
            input_image_bytes=image_bytes_with_text,
            test_id="ocr_test_doc"
        )
    except ImportError:
        print("Pillow (PIL) not installed. Skipping OCR test. Install with: pip install Pillow")
    except Exception as e:
        print(f"An error occurred during OCR test setup: {e}")

    # --- Test EntityRecognitionSkill (Collection(String) Output for various entity types) ---
    print("\n--- Testing EntityRecognitionSkill ---")
    entity_skill = EntityRecognitionSkill(
        inputs=[
            {"name": "text", "source": "/document/content"},
            {"name": "languageCode", "source": "/document/detectedLanguage"}
        ],
        outputs=[
            {"name": "organizations", "target_name": "recognizedOrganizations"},
            {"name": "persons", "target_name": "recognizedPersons"},
            {"name": "locations", "target_name": "recognizedLocations"}
        ],
        categories=["Organization", "Person", "Location"]
    )
    test_single_skill(
        entity_skill,
        input_text="Microsoft, founded by Bill Gates, has offices in Redmond, Washington.",
        test_id="entity_test_doc"
    )

    # --- Test SentimentSkill (String Output - "positive", "neutral", "negative") ---
    print("\n--- Testing SentimentSkill ---")
    sentiment_skill = SentimentSkill(
        inputs=[
            {"name": "text", "source": "/document/content"},
            {"name": "languageCode", "source": "/document/detectedLanguage"}
        ],
        outputs=[{"name": "sentiment", "target_name": "documentSentiment"}]
    )
    test_single_skill(
        sentiment_skill,
        input_text="The service provided was excellent, I am very satisfied!",
        test_id="sentiment_test_doc"
    )

    # --- Test PIIDetectionSkill (String Output - masked text) ---
    print("\n--- Testing PIIDetectionSkill ---")
    pii_skill = PIIDetectionSkill(
        inputs=[{"name": "text", "source": "/document/content"}],
        outputs=[{"name": "redactedText", "target_name": "maskedPiiText"}],
        masking_mode="replace",
        masking_character="*"
    )
    test_single_skill(
        pii_skill,
        input_text="My email is example@contoso.com and my phone number is 123-456-7890.",
        test_id="pii_test_doc"
    )

    # --- Test TextTranslationSkill (String Output) ---
    print("\n--- Testing TextTranslationSkill ---")
    translation_skill = TextTranslationSkill(
        inputs=[{"name": "text", "source": "/document/content"}],
        outputs=[{"name": "translatedText", "target_name": "translatedContent"}],
        target_language_code="fr" # Translate to French
    )
    test_single_skill(
        translation_skill,
        input_text="Hello, how are you?",
        test_id="translate_test_doc"
    )

    # --- Test ImageAnalysisSkill (Collection(String) Output for tags, or String for description) ---
    print("\n--- Testing ImageAnalysisSkill ---")
    try:
        # Create a simple image with a red square
        img_analysis = Image.new('RGB', (100, 100), color = 'red')
        img_analysis_byte_arr = BytesIO()
        img_analysis.save(img_analysis_byte_arr, format='PNG')
        image_bytes_for_analysis = img_analysis_byte_arr.getvalue()

        image_analysis_skill = ImageAnalysisSkill(
            inputs=[{"name": "image", "source": "/document/normalized_images/*"}],
            outputs=[
                {"name": "tags", "target_name": "imageTags"}, # Collection of strings
                {"name": "description", "target_name": "imageDescription"} # Single string
            ],
            visual_features=["Tags", "Description"] # Request tags and description
        )
        test_single_skill(
            image_analysis_skill,
            input_image_bytes=image_bytes_for_analysis,
            test_id="image_analysis_doc"
        )
    except ImportError:
        print("Pillow (PIL) not installed. Skipping ImageAnalysis test. Install with: pip install Pillow")
    except Exception as e:
        print(f"An error occurred during ImageAnalysis test setup: {e}")

    # --- Test AzureOpenAIEmbeddingSkill (Vector Output) ---
    if AOAI_RESOURCE_URI != "YOUR_AOAI_RESOURCE_URI" and AOAI_DEPLOYMENT_ID != "YOUR_AOAI_DEPLOYMENT_ID":
        print("\n--- Testing AzureOpenAIEmbeddingSkill (Vector Output) ---")
        try:
            embedding_skill = AzureOpenAIEmbeddingSkill(
                description="Embeddings for test",
                resource_uri=AOAI_RESOURCE_URI,
                deployment_id=AOAI_DEPLOYMENT_ID,
                inputs=[{"name": "text", "source": "/document/content"}],
                outputs=[{"name": "embedding", "target_name": "vectorOutput"}]
            )
            test_single_skill(
                embedding_skill,
                input_text="This is a sentence to be vectorized for embedding test.",
                test_id="embedding_test_doc",
                vector_dimensions=ADA_EMBEDDING_DIMENSIONS
            )
        except Exception as e:
            print(f"Error testing embedding skill. Ensure Azure OpenAI details are correct and key is set: {e}")
    else:
        print("\nSkipping AzureOpenAIEmbeddingSkill test: Azure OpenAI details (AOAI_RESOURCE_URI, AOAI_DEPLOYMENT_ID, ADA_EMBEDDING_DIMENSIONS) are not configured.")
