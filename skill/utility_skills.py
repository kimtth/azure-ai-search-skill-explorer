from .baseskill import BaseSkill, TextSkill
from azure.search.documents.indexes.models import (
    ConditionalSkill, MergeSkill, ShaperSkill, SplitSkill,
    OutputFieldMappingEntry, InputFieldMappingEntry
)


class ConditionalSkillTest(TextSkill):
    """Test ConditionalSkill for conditional logic."""
    
    def __init__(self):
        super().__init__("ConditionalSkill")
        self.requires_cognitive_services = False
        self.inputs = [
            InputFieldMappingEntry(name="condition", source="/document/language"),
            InputFieldMappingEntry(name="whenTrue", source="/document/content"),
            InputFieldMappingEntry(name="whenFalse", source="/document/content")
        ]
        self.outputs = [
            OutputFieldMappingEntry(name="output", target_name="conditionalOutput")
        ]
    
    def create_skill(self):
        return ConditionalSkill(
            inputs=self.inputs,
            outputs=self.outputs
        )
    
    def get_sample_input(self) -> str:
        return "This content will be processed conditionally based on language detection."


class MergeSkillTest(TextSkill):
    """Test MergeSkill for merging multiple text fields."""
    
    def __init__(self):
        super().__init__("MergeSkill")
        self.requires_cognitive_services = False
        self.inputs = [
            InputFieldMappingEntry(name="text", source="/document/content"),
            InputFieldMappingEntry(name="itemsToInsert", source="/document/normalized_images/*/text")
        ]
        self.outputs = [
            OutputFieldMappingEntry(name="mergedText", target_name="mergedContent")
        ]
    
    def create_skill(self):
        return MergeSkill(
            inputs=self.inputs,
            outputs=self.outputs,
            insert_pre_tag=" ",
            insert_post_tag=" "
        )


class ShaperSkillTest(TextSkill):
    """Test ShaperSkill for creating complex types."""
    
    def __init__(self):
        super().__init__("ShaperSkill")
        self.requires_cognitive_services = False
        # Override inputs for ShaperSkill
        self.inputs = [
            InputFieldMappingEntry(name="text", source="/document/content"),
            InputFieldMappingEntry(name="title", source="/document/metadata_title")
        ]
        self.outputs = [
            OutputFieldMappingEntry(name="output", target_name="shapedDocument")
        ]
    
    def create_skill(self):
        return ShaperSkill(
            inputs=self.inputs,
            outputs=self.outputs
        )
    
    def get_sample_input(self) -> str:
        return "Content to be shaped into a complex structure with metadata"


class SplitSkillTest(TextSkill):
    """Test SplitSkill for splitting text into chunks."""
    
    def __init__(self):
        super().__init__("SplitSkill")
        self.requires_cognitive_services = False
        self.outputs = [
            OutputFieldMappingEntry(name="textItems", target_name="pages")
        ]
    
    def create_skill(self):
        return SplitSkill(
            inputs=self.inputs,
            outputs=self.outputs,
            text_split_mode="pages",
            maximum_page_length=5000,
            page_overlap_length=100
        )
    
    def get_sample_input(self) -> str:
        # Create a long text that will be split
        return " ".join([
            f"This is paragraph {i}. " * 10
            for i in range(20)
        ])
