from .baseskill import TextSkill
from azure.search.documents.indexes.models import (
    LanguageDetectionSkill, KeyPhraseExtractionSkill, EntityRecognitionSkill,
    SentimentSkill, PIIDetectionSkill, TextTranslationSkill, EntityLinkingSkill,
    CustomEntityLookupSkill, OutputFieldMappingEntry, InputFieldMappingEntry,
    # VectorizeSkill
)


class LanguageDetectionSkillTest(TextSkill):
    def __init__(self):
        super().__init__("LanguageDetectionSkill")
        self.outputs = [
            OutputFieldMappingEntry(name="languageCode", target_name="detectedLanguage")
        ]
    
    def create_skill(self):
        return LanguageDetectionSkill(
            inputs=self.inputs,
            outputs=self.outputs
        )
    
    def get_sample_input(self) -> str:
        return "Hello, this is English. Bonjour, c'est français. Hola, esto es español."


class KeyPhraseExtractionSkillTest(TextSkill):
    def __init__(self):
        super().__init__("KeyPhraseExtractionSkill")
        self.outputs = [
            OutputFieldMappingEntry(name="keyPhrases", target_name="extractedKeyPhrases")
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
            OutputFieldMappingEntry(name="persons", target_name="recognizedPersons"),
            OutputFieldMappingEntry(name="organizations", target_name="recognizedOrganizations"),
            OutputFieldMappingEntry(name="locations", target_name="recognizedLocations")
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
            OutputFieldMappingEntry(name="sentiment", target_name="documentSentiment")
        ]
    
    def create_skill(self):
        return SentimentSkill(
            inputs=self.inputs,
            outputs=self.outputs
        )
    
    def get_sample_input(self) -> str:
        return "The service was absolutely fantastic! I'm very happy with the results."


class PIIDetectionSkillTest(TextSkill):
    def __init__(self):
        super().__init__("PIIDetectionSkill")
        self.outputs = [
            OutputFieldMappingEntry(name="piiEntities", target_name="detectedPII"),
            OutputFieldMappingEntry(name="maskedText", target_name="maskedText")
        ]
    
    def create_skill(self):
        return PIIDetectionSkill(
            inputs=self.inputs,
            outputs=self.outputs
        )
    
    def get_sample_input(self) -> str:
        return "John Doe's email is john.doe@example.com and his phone is 555-123-4567."


class TextTranslationSkillTest(TextSkill):
    def __init__(self):
        super().__init__("TextTranslationSkill")
        self.outputs = [
            OutputFieldMappingEntry(name="translatedText", target_name="translatedContent")
        ]
    
    def create_skill(self):
        return TextTranslationSkill(
            inputs=self.inputs,
            outputs=self.outputs,
            default_to_language_code="es"  # Spanish
        )
    
    def get_sample_input(self) -> str:
        return "Hello world! How are you today?"


class EntityLinkingSkillTest(TextSkill):
    def __init__(self):
        super().__init__("EntityLinkingSkill")
        self.outputs = [
            OutputFieldMappingEntry(name="entities", target_name="linkedEntities")
        ]
    
    def create_skill(self):
        return EntityLinkingSkill(
            inputs=self.inputs,
            outputs=self.outputs
        )
    
    def get_sample_input(self) -> str:
        return "Microsoft was founded by Bill Gates in Redmond. Apple was founded by Steve Jobs."


class CustomEntityLookupSkillTest(TextSkill):
    def __init__(self):
        super().__init__("CustomEntityLookupSkill")
        self.outputs = [
            OutputFieldMappingEntry(name="entities", target_name="customEntities")
        ]
    
    def create_skill(self):
        return CustomEntityLookupSkill(
            inputs=self.inputs,
            outputs=self.outputs,
            entities_definition_uri="https://example.com/entities.csv"  # Would need real URI
        )


class VectorizeSkillTest(TextSkill):
    def __init__(self):
        super().__init__("VectorizeSkill")
        self.has_vector_output = True
        self.vector_dimensions = 1024  # Default dimensions
        self.outputs = [
            OutputFieldMappingEntry(name="vector", target_name="textVector")
        ]
    
    def create_skill(self):
        # Note: VectorizeSkill parameters may vary based on Azure AI Search version
        # This is a basic configuration
        # TODO
        pass
        # try:
        #     return VectorizeSkill(
        #         inputs=self.inputs,
        #         outputs=self.outputs
        #     )
        # except Exception as e:
        #     # Fallback if specific parameters are required
        #     print(f"VectorizeSkill creation failed: {e}")
        #     raise
    
    def get_sample_input(self) -> str:
        return "This text will be converted to a vector representation using Azure AI."
