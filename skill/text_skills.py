from .baseskill import TextSkill
from azure.search.documents.indexes.models import (
    LanguageDetectionSkill,
    KeyPhraseExtractionSkill,
    EntityRecognitionSkill,
    SentimentSkill,
    PIIDetectionSkill,
    TextTranslationSkill,
    EntityLinkingSkill,
    # CustomEntityLookupSkill,
    OutputFieldMappingEntry,
)


class LanguageDetectionSkillTest(TextSkill):
    def __init__(self, default_country_hint: str = None):
        super().__init__("LanguageDetectionSkill")
        self.default_country_hint = default_country_hint
        self.outputs = [
            OutputFieldMappingEntry(name="languageCode", target_name="content_output")
        ]

    def create_skill(self):
        return LanguageDetectionSkill(
            default_country_hint=self.default_country_hint,
            inputs=self.inputs,
            outputs=self.outputs,
        )


class KeyPhraseExtractionSkillTest(TextSkill):
    def __init__(
        self,
        default_language_code: str = None,
        max_key_phrase_count: int = None,
        model_version: str = None,
    ):
        super().__init__("KeyPhraseExtractionSkill")
        self.default_language_code = default_language_code
        self.max_key_phrase_count = max_key_phrase_count
        self.model_version = model_version
        self.outputs = [
            OutputFieldMappingEntry(name="keyPhrases", target_name="collection_output")
        ]

    def create_skill(self):
        return KeyPhraseExtractionSkill(
            default_language_code=self.default_language_code,
            max_key_phrase_count=self.max_key_phrase_count,
            model_version=self.model_version,
            inputs=self.inputs,
            outputs=self.outputs,
        )


class EntityRecognitionSkillTest(TextSkill):
    def __init__(
        self,
        categories: list = None,
        default_language_code: str = None,
        minimum_precision: float = None,
        model_version: str = None,
    ):
        super().__init__("EntityRecognitionSkill")
        self.categories = categories or ["Person", "Organization", "Location"]
        self.default_language_code = default_language_code
        self.minimum_precision = minimum_precision
        self.model_version = model_version
        self.outputs = [
            OutputFieldMappingEntry(name="persons", target_name="collection_output"),
            OutputFieldMappingEntry(
                name="organizations", target_name="collection_output"
            ),
            OutputFieldMappingEntry(name="locations", target_name="collection_output"),
        ]

    def create_skill(self):
        return EntityRecognitionSkill(
            categories=self.categories,
            default_language_code=self.default_language_code,
            minimum_precision=self.minimum_precision,
            model_version=self.model_version,
            inputs=self.inputs,
            outputs=self.outputs,
        )


class SentimentSkillTest(TextSkill):
    def __init__(
        self,
        default_language_code: str = None,
        include_opinion_mining: bool = False,
        model_version: str = None,
    ):
        super().__init__("SentimentSkill")
        self.default_language_code = default_language_code
        self.include_opinion_mining = include_opinion_mining
        self.model_version = model_version
        self.outputs = [
            OutputFieldMappingEntry(name="sentiment", target_name="content_output")
        ]

    def create_skill(self):
        return SentimentSkill(
            default_language_code=self.default_language_code,
            include_opinion_mining=self.include_opinion_mining,
            model_version=self.model_version,
            inputs=self.inputs,
            outputs=self.outputs,
        )


class PIIDetectionSkillTest(TextSkill):
    def __init__(
        self,
        default_language_code: str = None,
        minimum_precision: float = None,
        masking_mode: str = None,
        masking_character: str = None,
        domain: str = None,
        pii_categories: list = None,
    ):
        super().__init__("PIIDetectionSkill")
        self.default_language_code = default_language_code
        self.minimum_precision = minimum_precision
        self.masking_mode = masking_mode
        self.masking_character = masking_character
        self.domain = domain
        self.pii_categories = pii_categories
        self.outputs = [
            OutputFieldMappingEntry(
                name="piiEntities", target_name="collection_output"
            ),
            OutputFieldMappingEntry(name="maskedText", target_name="content_output"),
        ]

    def create_skill(self):
        return PIIDetectionSkill(
            default_language_code=self.default_language_code,
            minimum_precision=self.minimum_precision,
            masking_mode=self.masking_mode,
            masking_character=self.masking_character,
            domain=self.domain,
            pii_categories=self.pii_categories,
            inputs=self.inputs,
            outputs=self.outputs,
        )


class TextTranslationSkillTest(TextSkill):
    def __init__(
        self,
        default_to_language_code: str,
        default_from_language_code: str = None,
        suggested_from: str = None,
    ):
        super().__init__("TextTranslationSkill")
        self.default_to_language_code = default_to_language_code
        self.default_from_language_code = default_from_language_code
        self.suggested_from = suggested_from
        self.outputs = [
            OutputFieldMappingEntry(name="translatedText", target_name="content_output")
        ]

    def create_skill(self):
        return TextTranslationSkill(
            default_to_language_code=self.default_to_language_code,
            default_from_language_code=self.default_from_language_code,
            suggested_from=self.suggested_from,
            inputs=self.inputs,
            outputs=self.outputs,
        )


class EntityLinkingSkillTest(TextSkill):
    def __init__(
        self,
        default_language_code: str = None,
        minimum_precision: float = None,
        model_version: str = None,
    ):
        super().__init__("EntityLinkingSkill")
        self.default_language_code = default_language_code
        self.minimum_precision = minimum_precision
        self.model_version = model_version
        self.outputs = [
            OutputFieldMappingEntry(name="entities", target_name="collection_output")
        ]

    def create_skill(self):
        return EntityLinkingSkill(
            default_language_code=self.default_language_code,
            minimum_precision=self.minimum_precision,
            model_version=self.model_version,
            inputs=self.inputs,
            outputs=self.outputs,
        )



