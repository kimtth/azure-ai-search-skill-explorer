from .baseskill import BaseSkill
from azure.search.documents.indexes.models import (
    DocumentExtractionSkill, # DocumentIntelligenceLayoutSkill,
    OutputFieldMappingEntry, InputFieldMappingEntry
)


class DocumentExtractionSkillTest(BaseSkill):
    """Test DocumentExtractionSkill for extracting content from documents."""
    
    def __init__(self):
        super().__init__("DocumentExtractionSkill")
        self.inputs = [
            InputFieldMappingEntry(name="file_data", source="/document/file_data")
        ]
        self.outputs = [
            OutputFieldMappingEntry(name="content", target_name="extractedContent")
        ]
        self.requires_cognitive_services = False
    
    def create_skill(self):
        return DocumentExtractionSkill(
            inputs=self.inputs,
            outputs=self.outputs
        )
    
    def get_sample_input(self) -> str:
        # Return text instead of bytes for blob storage compatibility
        return "Sample document content for extraction testing"


class DocumentIntelligenceLayoutSkillTest(BaseSkill):
    """Test DocumentIntelligenceLayoutSkill for document layout analysis."""
    
    def __init__(self):
        super().__init__("DocumentIntelligenceLayoutSkill")
        self.inputs = [
            InputFieldMappingEntry(name="file_data", source="/document/file_data")
        ]
        self.outputs = [
            OutputFieldMappingEntry(name="content", target_name="layoutText")
        ]
    
    def create_skill(self):
        try:
            # TODO
            pass
        except ImportError:
            print("DocumentIntelligenceLayoutSkill not available in this Azure Search SDK version")
            raise
    
    def get_sample_input(self) -> str:
        return "Sample document with complex layout for analysis"
    
    def get_sample_input(self) -> bytes:
        """Return a document with complex layout for testing."""
        return b"Document with tables and figures"
