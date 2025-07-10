from .baseskill import TextSkill
from azure.search.documents.indexes.models import (
    LanguageDetectionSkill, KeyPhraseExtractionSkill, EntityRecognitionSkill,
    SentimentSkill, PIIDetectionSkill, TextTranslationSkill, EntityLinkingSkill,
    CustomEntityLookupSkill, OutputFieldMappingEntry, VisionVectorizeSkill
)


class LanguageDetectionSkillTest(TextSkill):
    def __init__(self):
        super().__init__("LanguageDetectionSkill")
        self.outputs = [
            OutputFieldMappingEntry(name="languageCode", target_name="content_output")
        ]
    
    def create_skill(self):
        return LanguageDetectionSkill(
            inputs=self.inputs,
            outputs=self.outputs
        )
    

class KeyPhraseExtractionSkillTest(TextSkill):
    def __init__(self):
        super().__init__("KeyPhraseExtractionSkill")
        self.outputs = [
            OutputFieldMappingEntry(name="keyPhrases", target_name="collection_output")
        ]
    
    def create_skill(self):
        return KeyPhraseExtractionSkill(
            inputs=self.inputs,
            outputs=self.outputs
        )


class EntityRecognitionSkillTest(TextSkill):
    def __init__(self):
        super().__init__("EntityRecognitionSkill")
        self.outputs = [
            OutputFieldMappingEntry(name="persons", target_name="collection_output"),
            OutputFieldMappingEntry(name="organizations", target_name="collection_output"),
            OutputFieldMappingEntry(name="locations", target_name="collection_output")
        ]
    
    def create_skill(self):
        return EntityRecognitionSkill(
            inputs=self.inputs,
            outputs=self.outputs,
            categories=["Person", "Organization", "Location"]
        )


class SentimentSkillTest(TextSkill):
    def __init__(self):
        super().__init__("SentimentSkill")
        self.outputs = [
            OutputFieldMappingEntry(name="sentiment", target_name="content_output")
        ]
    
    def create_skill(self):
        return SentimentSkill(
            inputs=self.inputs,
            outputs=self.outputs
        )


class PIIDetectionSkillTest(TextSkill):
    def __init__(self):
        super().__init__("PIIDetectionSkill")
        self.outputs = [
            OutputFieldMappingEntry(name="piiEntities", target_name="collection_output"),
            OutputFieldMappingEntry(name="maskedText", target_name="content_output")
        ]
    
    def create_skill(self):
        return PIIDetectionSkill(
            inputs=self.inputs,
            outputs=self.outputs
        )


class TextTranslationSkillTest(TextSkill):
    def __init__(self):
        super().__init__("TextTranslationSkill")
        self.outputs = [
            OutputFieldMappingEntry(name="translatedText", target_name="content_output")
        ]
    
    def create_skill(self):
        return TextTranslationSkill(
            inputs=self.inputs,
            outputs=self.outputs,
            default_to_language_code="es"  # Spanish
        )
    

class EntityLinkingSkillTest(TextSkill):
    def __init__(self):
        super().__init__("EntityLinkingSkill")
        self.outputs = [
            OutputFieldMappingEntry(name="entities", target_name="collection_output")
        ]
    
    def create_skill(self):
        return EntityLinkingSkill(
            inputs=self.inputs,
            outputs=self.outputs
        )


class CustomEntityLookupSkillTest(TextSkill):
    def __init__(self):
        super().__init__("CustomEntityLookupSkill")
        self.outputs = [
            OutputFieldMappingEntry(name="entities", target_name="collection_output")
        ]
    
    def create_skill(self):
        return CustomEntityLookupSkill(
            inputs=self.inputs,
            outputs=self.outputs,
            entities_definition_uri="https://example.com/entities.csv"  # Would need real URI
        )


class VisionVectorizeSkillTest(TextSkill):
    def __init__(self):
        super().__init__("VisionVectorizeSkill")
        self.has_vector_output = True
        self.outputs = [
            OutputFieldMappingEntry(name="vector", target_name="vector_output")
        ]
    
    def create_skill(self):
        # Note: VisionVectorizeSkill parameters may vary based on Azure AI Search version
        # This is a basic configuration
        try:
            return VisionVectorizeSkill(
                inputs=self.inputs,
                outputs=self.outputs
            )
        except Exception as e:
            # Fallback if specific parameters are required
            print(f"VisionVectorizeSkill creation failed: {e}")
            raise
