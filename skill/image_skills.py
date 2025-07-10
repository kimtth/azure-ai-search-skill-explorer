from .baseskill import ImageSkill
from azure.search.documents.indexes.models import (
    OcrSkill, ImageAnalysisSkill, OutputFieldMappingEntry
)


class OcrSkillTest(ImageSkill):
    def __init__(self):
        super().__init__("OcrSkill")
        self.outputs = [
            OutputFieldMappingEntry(name="text", target_name="content_output")
        ]
    
    def create_skill(self):
        return OcrSkill(
            inputs=self.inputs,
            outputs=self.outputs
        )


class ImageAnalysisSkillTest(ImageSkill):
    def __init__(self):
        super().__init__("ImageAnalysisSkill")
        self.outputs = [
            OutputFieldMappingEntry(name="tags", target_name="collection_output"),
            OutputFieldMappingEntry(name="description", target_name="content_output")
        ]
    
    def create_skill(self):
        return ImageAnalysisSkill(
            inputs=self.inputs,
            outputs=self.outputs,
            visual_features=["Tags", "Description"]
        )
    
