from dotenv import load_dotenv
import os
load_dotenv()

from .baseskill import ImageSkill
from azure.search.documents.indexes.models import (
    OcrSkill, ImageAnalysisSkill, OutputFieldMappingEntry,
    VisionVectorizeSkill
)

class OcrSkillTest(ImageSkill):
    def __init__(self,
        default_language_code: str = None,
        detect_orientation: bool = True,
        line_ending: str = None
    ):
        super().__init__("OcrSkill")
        self.default_language_code = default_language_code
        self.detect_orientation = detect_orientation
        self.line_ending = line_ending
        self.outputs = [
            OutputFieldMappingEntry(name="text", target_name="content_output")
        ]
    
    def create_skill(self):
        return OcrSkill(
            default_language_code=self.default_language_code,
            detect_orientation=self.detect_orientation,
            line_ending=self.line_ending,
            inputs=self.inputs,
            outputs=self.outputs
        )

class ImageAnalysisSkillTest(ImageSkill):
    def __init__(self,
        default_language_code: str = "en",
        visual_features: list = None,
        details: list = None
    ):
        super().__init__("ImageAnalysisSkill")
        self.default_language_code = default_language_code
        self.visual_features = visual_features or ["tags", "description"]
        self.details = details or []
        self.outputs = [
            OutputFieldMappingEntry(name="tags", target_name="collection_output"),
            OutputFieldMappingEntry(name="description", target_name="content_output")
        ]
    
    def create_skill(self):
        return ImageAnalysisSkill(
            default_language_code=self.default_language_code,
            visual_features=self.visual_features,
            details=self.details,
            inputs=self.inputs,
            outputs=self.outputs
        )


class VisionVectorizeSkillTest(ImageSkill):
    def __init__(self, model_version: str = "2023-04-15"):
        super().__init__("VisionVectorizeSkill")
        self.has_vector_output = True
        self.model_version = model_version
        self.outputs = [
            OutputFieldMappingEntry(name="vector", target_name="vector_output")
        ]

    def create_skill(self):
        return VisionVectorizeSkill(
            model_version=self.model_version, inputs=self.inputs, outputs=self.outputs
        )