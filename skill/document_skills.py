from .baseskill import BaseSkill
from azure.search.documents.indexes.models import (
    DocumentExtractionSkill, DocumentIntelligenceLayoutSkill,
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
            OutputFieldMappingEntry(name="content", target_name="content_output")
        ]
        self.requires_cognitive_services = False
    
    def create_skill(self):
        return DocumentExtractionSkill(
            inputs=self.inputs,
            outputs=self.outputs
        )


class DocumentIntelligenceLayoutSkillTest(BaseSkill):
    """Test DocumentIntelligenceLayoutSkill for document layout analysis."""
    
    def __init__(self):
        super().__init__("DocumentIntelligenceLayoutSkill")
        self.inputs = [
            InputFieldMappingEntry(name="file_data", source="/document/file_data")
        ]
        # switch to markdown output
        self.outputs = [
            OutputFieldMappingEntry(name="markdown_document", target_name="layout_output")
        ]
    
    def create_skill(self):
        try:
            return DocumentIntelligenceLayoutSkill(
                inputs=self.inputs,
                outputs=self.outputs,
                output_mode="oneToMany",
                markdown_header_depth="h3"
            )
        except ImportError:
            print("DocumentIntelligenceLayoutSkill not available in this SDK version")
            raise
    

