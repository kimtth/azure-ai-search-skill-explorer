from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexClient, SearchIndexerClient
from azure.search.documents.indexes.models import (
    SearchIndexer,
    SearchIndexerDataSourceConnection,
    SearchIndexerSkillset,
    SearchField,
    SearchFieldDataType,
    IndexingParameters,
    SearchIndex,
    FieldMapping,
    CognitiveServicesAccountKey,
    VectorSearch,
    HnswAlgorithmConfiguration,
    VectorSearchProfile,
)
from azure.search.documents import SearchClient


class AiSearchController:
    def __init__(self, service_name: str, admin_key: str, query_key: str):
        endpoint = f"https://{service_name}.search.windows.net/"
        self.admin_cred = AzureKeyCredential(admin_key)
        self.query_cred = AzureKeyCredential(query_key)
        self.index_client = SearchIndexClient(endpoint, self.admin_cred)
        self.indexer_client = SearchIndexerClient(endpoint, self.admin_cred)
        self.endpoint = endpoint

    def create_data_source(
        self, ds_name: str, connection_string: str, container_name: str
    ):
        ds = self.indexer_client.get_data_source_connection(ds_name)
        if ds:
            return
        data_source = SearchIndexerDataSourceConnection(
            name=ds_name,
            type="azureblob",
            connection_string=connection_string,
            container={"name": container_name},
        )
        self.index_client.create_or_update_data_source_connection(data_source)

    def create_skillset(self, skillset_name: str, skills: list, cognitive_key: str):
        sks = self.indexer_client.get_skillset(skillset_name)
        if sks:
            return
        skillset = SearchIndexerSkillset(
            name=skillset_name,
            description="Skillset for testing",
            skills=skills,
            cognitive_services_account=CognitiveServicesAccountKey(key=cognitive_key),
        )
        self.index_client.create_or_update_skillset(skillset)

    def create_index(
        self, index_name: str, has_vector: bool = False, vector_dims: int = None
    ):
        idx = self.index_client.get_index(index_name)
        if idx:
            return
        fields = [
            SearchField(name="id", type=SearchFieldDataType.String, key=True),
            SearchField(
                name="content", type=SearchFieldDataType.String, searchable=True
            ),
            SearchField(
                name="content_output", type=SearchFieldDataType.String, searchable=True
            ),
            SearchField(
                name="collection_output",
                type=SearchFieldDataType.Collection(SearchFieldDataType.String),
                searchable=True,
            ),
        ]
        vector_search = None
        if has_vector and vector_dims:
            fields.append(
                SearchField(
                    name="vector_output",
                    type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                    searchable=True,
                    vector_search_dimensions=vector_dims,
                    vector_search_profile_name="my-vector-profile",
                )
            )
            vector_search = VectorSearch(
                profiles=[
                    VectorSearchProfile(
                        name="my-vector-profile", algorithm_configuration_name="my-hnsw"
                    )
                ],
                algorithms=[HnswAlgorithmConfiguration(name="my-hnsw")],
            )
        index = SearchIndex(name=index_name, fields=fields, vector_search=vector_search)
        self.index_client.create_or_update_index(index)

    def create_and_run_indexer(
        self,
        indexer_name: str,
        ds_name: str,
        skillset_name: str,
        index_name: str,
        output_mappings: list,
        needs_images: bool = False,
    ):
        idxr = self.indexer_client.get_indexer(indexer_name)
        if idxr:
            return
        field_mappings = [
            FieldMapping(
                source_field_name="metadata_storage_path",
                target_field_name="id",
                mapping_function={"name": "base64Encode"},
            ),
            FieldMapping(source_field_name="content", target_field_name="content"),
        ]
        parameters = IndexingParameters(
            batch_size=1, max_failed_items=-1, max_failed_items_per_batch=-1
        )
        if needs_images:
            parameters.configuration = {
                "dataToExtract": "contentAndMetadata",
                "imageAction": "generateNormalizedImages",
            }
        indexer = SearchIndexer(
            name=indexer_name,
            data_source_name=ds_name,
            skillset_name=skillset_name,
            target_index_name=index_name,
            field_mappings=field_mappings,
            output_field_mappings=output_mappings,
            parameters=parameters,
        )
        self.index_client.create_or_update_indexer(indexer)
        self.index_client.run_indexer(indexer_name)
        self.wait_for_indexer(indexer_name)

    def wait_for_indexer(self, indexer_name: str, timeout: int = 60):
        import time

        start = time.time()
        while time.time() - start < timeout:
            status = self.indexer_client.get_indexer_status(indexer_name)
            if status.last_result and status.last_result.status in [
                "unknown",
                "running",
                "error",
            ]:
                return
            time.sleep(2)

    def fetch_results(self, index_name: str):
        client = SearchClient(self.endpoint, index_name, self.query_cred)
        results = []
        for r in client.search(search_text="*", include_total_count=True):
            results.append({k: v for k, v in r.items() if not k.startswith("@")})
        return results

    def cleanup_resources(self, resources: dict):
        for t, key in [
            ("indexer", "indexer_name"),
            ("index", "index_name"),
            ("skillset", "skillset_name"),
            ("data_source", "ds_name"),
        ]:
            name = resources[key]
            try:
                if t == "indexer":
                    self.index_client.delete_indexer(name)
                elif t == "index":
                    self.index_client.delete_index(name)
                elif t == "skillset":
                    self.index_client.delete_skillset(name)
                else:
                    self.index_client.delete_data_source_connection(name)
            except:
                pass
