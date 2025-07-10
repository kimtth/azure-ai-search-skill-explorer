from typing import Union
from azure.storage.blob import BlobServiceClient

class BlobController:
    def __init__(self, account_name: str, account_key: str, container_name: str):
        self.account_name = account_name
        self.account_key = account_key
        self.container_name = container_name

    def get_connection_string(self) -> str:
        return (
            f"DefaultEndpointsProtocol=https;"
            f"AccountName={self.account_name};"
            f"AccountKey={self.account_key};"
            f"EndpointSuffix=core.windows.net"
        )

    def upload_test_data(self, content: Union[str, bytes], test_id: str, is_image: bool = False) -> str:
        blob_service_client = BlobServiceClient.from_connection_string(self.get_connection_string())
        container_client = blob_service_client.get_container_client(self.container_name)
        try:
            container_client.create_container()
        except Exception as e:
            if "ContainerAlreadyExists" not in str(e):
                raise e

        extension = "jpg" if is_image else "txt"
        blob_path = f"test_data/{test_id}/input.{extension}"
        blob_client = container_client.get_blob_client(blob_path)

        if isinstance(content, str):
            content = content.encode("utf-8")
        blob_client.upload_blob(content, overwrite=True)
        return blob_path