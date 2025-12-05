"""Skill preview engine - shows realistic Azure AI Search index results based on official skill output schemas."""

import json
from typing import Dict, Any
from skill.sample_data import get_sample_for_skill, is_image_skill


class SkillPreviewEngine:
    """Preview skill outputs showing how data would be stored in Azure AI Search index."""
    
    def preview_skill(self, skill_name: str, input_text: str = None) -> Dict[str, Any]:
        """Generate preview output matching Azure AI Search index document format."""
        text = input_text or get_sample_for_skill(skill_name)
        
        handlers = {
            "LanguageDetectionSkill": self._preview_language_detection,
            "KeyPhraseExtractionSkill": self._preview_key_phrase,
            "EntityRecognitionSkill": self._preview_entity_recognition,
            "SentimentSkill": self._preview_sentiment,
            "PIIDetectionSkill": self._preview_pii,
            "TextTranslationSkill": self._preview_translation,
            "EntityLinkingSkill": self._preview_entity_linking,
            "SplitSkill": self._preview_split,
            "MergeSkill": self._preview_merge,
            "ShaperSkill": self._preview_shaper,
            "ConditionalSkill": self._preview_conditional,
            "OcrSkill": self._preview_ocr,
            "ImageAnalysisSkill": self._preview_image_analysis,
            "VisionVectorizeSkill": self._preview_vision_vectorize,
            "DocumentExtractionSkill": self._preview_document_extraction,
            "DocumentIntelligenceLayoutSkill": self._preview_doc_intelligence,
            "AzureOpenAIEmbeddingSkill": self._preview_embedding,
        }
        
        handler = handlers.get(skill_name, self._preview_generic)
        
        # Build sample input based on skill type
        if is_image_skill(skill_name):
            sample_input = {
                "recordId": "1",
                "data": {"imageUrl": f"file:///{text.replace(chr(92), '/')}"} if text.startswith(('D:', 'C:', '/')) else {"imageUrl": text}
            }
        else:
            sample_input = {
                "recordId": "1",
                "data": {"text": text[:500] + "..." if len(text) > 500 else text}
            }
        
        return {
            "skillDefinition": self._get_skill_definition(skill_name),
            "sampleInput": sample_input,
            "indexDocument": handler(text)
        }
    
    def _get_skill_definition(self, skill_name: str) -> Dict:
        """Return official @odata.type for the skill."""
        odata_types = {
            "LanguageDetectionSkill": "#Microsoft.Skills.Text.LanguageDetectionSkill",
            "KeyPhraseExtractionSkill": "#Microsoft.Skills.Text.KeyPhraseExtractionSkill",
            "EntityRecognitionSkill": "#Microsoft.Skills.Text.V3.EntityRecognitionSkill",
            "SentimentSkill": "#Microsoft.Skills.Text.V3.SentimentSkill",
            "PIIDetectionSkill": "#Microsoft.Skills.Text.PIIDetectionSkill",
            "TextTranslationSkill": "#Microsoft.Skills.Text.TranslationSkill",
            "EntityLinkingSkill": "#Microsoft.Skills.Text.V3.EntityLinkingSkill",
            "SplitSkill": "#Microsoft.Skills.Text.SplitSkill",
            "MergeSkill": "#Microsoft.Skills.Text.MergeSkill",
            "ShaperSkill": "#Microsoft.Skills.Util.ShaperSkill",
            "ConditionalSkill": "#Microsoft.Skills.Util.ConditionalSkill",
            "OcrSkill": "#Microsoft.Skills.Vision.OcrSkill",
            "ImageAnalysisSkill": "#Microsoft.Skills.Vision.ImageAnalysisSkill",
            "VisionVectorizeSkill": "#Microsoft.Skills.Vision.VectorizeSkill",
            "DocumentExtractionSkill": "#Microsoft.Skills.Util.DocumentExtractionSkill",
            "DocumentIntelligenceLayoutSkill": "#Microsoft.Skills.Util.DocumentIntelligenceLayoutSkill",
            "AzureOpenAIEmbeddingSkill": "#Microsoft.Skills.Text.AzureOpenAIEmbeddingSkill",
        }
        return {"@odata.type": odata_types.get(skill_name, "Unknown")}
    
    def _preview_language_detection(self, text: str) -> Dict:
        """Official output: languageCode, languageName, score"""
        return {
            "id": "doc_001",
            "content": text[:200],
            "languageCode": "en",
            "languageName": "English",
            "score": 1.0
        }
    
    def _preview_key_phrase(self, text: str) -> Dict:
        """Official output: keyPhrases (array of strings, ordered by importance)"""
        return {
            "id": "doc_001",
            "content": text[:200],
            "keyPhrases": [
                "Azure AI Search",
                "cloud search service",
                "search experience",
                "private heterogeneous content",
                "Microsoft Azure",
                "enterprise applications"
            ]
        }
    
    def _preview_entity_recognition(self, text: str) -> Dict:
        """Official output: persons, locations, organizations, namedEntities (with confidence scores)"""
        return {
            "id": "doc_001",
            "content": text[:200],
            "persons": ["John Smith", "Satya Nadella"],
            "locations": ["Redmond", "Washington", "San Francisco"],
            "organizations": ["Microsoft", "Contoso Ltd", "Azure"],
            "namedEntities": [
                {"text": "John Smith", "category": "Person", "subcategory": None, "confidenceScore": 0.98, "offset": 0, "length": 10},
                {"text": "Microsoft", "category": "Organization", "subcategory": None, "confidenceScore": 0.99, "offset": 50, "length": 9},
                {"text": "Redmond", "category": "Location", "subcategory": "GPE", "confidenceScore": 0.95, "offset": 120, "length": 7}
            ]
        }
    
    def _preview_sentiment(self, text: str) -> Dict:
        """Official output: sentiment, confidenceScores, sentences (with opinion mining)"""
        return {
            "id": "doc_001",
            "content": text[:200],
            "sentiment": "positive",
            "confidenceScores": {"positive": 0.89, "neutral": 0.10, "negative": 0.01},
            "sentences": [
                {
                    "text": "Azure AI Search is a cloud search service that gives developers infrastructure.",
                    "sentiment": "positive",
                    "confidenceScores": {"positive": 0.92, "neutral": 0.07, "negative": 0.01},
                    "offset": 0,
                    "length": 78,
                    "targets": [],
                    "assessments": []
                }
            ]
        }
    
    def _preview_pii(self, text: str) -> Dict:
        """Official output: piiEntities (with type, subtype, score, offset, length), maskedText"""
        return {
            "id": "doc_001",
            "content": text[:200],
            "piiEntities": [
                {"text": "john.smith@contoso.com", "type": "Email", "subtype": "", "score": 0.99, "offset": 150, "length": 22},
                {"text": "+1-425-555-0123", "type": "PhoneNumber", "subtype": "", "score": 0.95, "offset": 180, "length": 15},
                {"text": "859-98-0987", "type": "U.S. Social Security Number (SSN)", "subtype": "", "score": 0.85, "offset": 210, "length": 11}
            ],
            "maskedText": "Contact: ******************** at *************** SSN: ***********"
        }
    
    def _preview_translation(self, text: str) -> Dict:
        """Official output: translatedText, translatedToLanguageCode"""
        return {
            "id": "doc_001",
            "content": text[:200],
            "translatedText": "Azure AI Search es un servicio de búsqueda en la nube que ofrece a los desarrolladores infraestructura, API y herramientas.",
            "translatedToLanguageCode": "es"
        }
    
    def _preview_entity_linking(self, text: str) -> Dict:
        """Official output: entities (with name, matches, url, dataSource)"""
        return {
            "id": "doc_001",
            "content": text[:200],
            "entities": [
                {
                    "name": "Microsoft",
                    "matches": [{"text": "Microsoft", "offset": 0, "length": 9, "confidenceScore": 0.98}],
                    "language": "en",
                    "id": "Microsoft",
                    "url": "https://en.wikipedia.org/wiki/Microsoft",
                    "dataSource": "Wikipedia"
                },
                {
                    "name": "Microsoft Azure",
                    "matches": [{"text": "Azure", "offset": 50, "length": 5, "confidenceScore": 0.95}],
                    "language": "en",
                    "id": "Microsoft_Azure",
                    "url": "https://en.wikipedia.org/wiki/Microsoft_Azure",
                    "dataSource": "Wikipedia"
                }
            ]
        }
    
    def _preview_split(self, text: str) -> Dict:
        """Official output: textItems (array of text chunks)"""
        return {
            "id": "doc_001",
            "content": text[:200],
            "textItems": [
                "Azure AI Search (formerly known as Azure Cognitive Search) is a cloud search service...",
                "Microsoft Azure was announced in October 2008 and released on February 1, 2010...",
                "Azure provides more than 200 products and cloud services designed to help bring new solutions..."
            ]
        }
    
    def _preview_merge(self, text: str) -> Dict:
        """Official output: mergedText"""
        return {
            "id": "doc_001",
            "content": text[:200],
            "mergedText": text + " [OCR extracted text from embedded images would be merged here]"
        }
    
    def _preview_shaper(self, text: str) -> Dict:
        """Official output: output (complex type with custom shape)"""
        return {
            "id": "doc_001",
            "content": text[:200],
            "shapedOutput": {
                "documentInfo": {
                    "title": "Azure AI Search Overview",
                    "content": text[:100],
                    "metadata": {"wordCount": len(text.split()), "charCount": len(text)}
                }
            }
        }
    
    def _preview_conditional(self, text: str) -> Dict:
        """Official output: output (based on condition evaluation)"""
        return {
            "id": "doc_001",
            "content": text[:200],
            "conditionalOutput": text if len(text) > 100 else "[Content too short - default value applied]"
        }
    
    def _preview_ocr(self, image_url: str) -> Dict:
        """Official output: text, layoutText - simulates OCR on sample invoice"""
        return {
            "id": "doc_001",
            "content": f"[Image: {image_url.split('/')[-1]}]",
            "text": """CONTOSO LTD.
INVOICE

Invoice Number: INV-100
Invoice Date: November 15, 2019
Invoice Due Date: December 15, 2019
Charges: $110.00
VAT ID: GB123456789

From:
Contoso Consulting Ltd
123 456th St
New York, NY 10001

To:
Microsoft Finance Department
1020 Enterprise Way
Sunnyville, CA 87659

Service Period: 11/4/2019 - 11/15/2019
Consultant: John Smith
Total Hours: 10 @ $10.00/hr = $100.00
Amount Due: $110.00

Thank you for your business.""",
            "layoutText": """CONTOSO LTD.                                    INVOICE

Invoice Number: INV-100           Invoice Date: November 15, 2019
                                  Invoice Due Date: December 15, 2019
Charges: $110.00                  VAT ID: GB123456789

From:                             To:
Contoso Consulting Ltd            Microsoft Finance Department
123 456th St                      1020 Enterprise Way
New York, NY 10001                Sunnyville, CA 87659

-----------------------------------------------------------------
Service Period        Consultant       Hours    Rate     Amount
11/4/2019-11/15/2019  John Smith       10       $10.00   $100.00
-----------------------------------------------------------------
                                        Amount Due:      $110.00"""
        }
    
    def _preview_image_analysis(self, image_url: str) -> Dict:
        """Official output: tags, description, categories, etc. - simulates analysis of Empire State Building"""
        return {
            "id": "doc_001",
            "content": f"[Image: {image_url.split('/')[-1]}]",
            "tags": [
                {"name": "building", "confidence": 0.99},
                {"name": "skyscraper", "confidence": 0.98},
                {"name": "city", "confidence": 0.97},
                {"name": "architecture", "confidence": 0.95},
                {"name": "outdoor", "confidence": 0.94},
                {"name": "tower", "confidence": 0.92},
                {"name": "sky", "confidence": 0.88},
                {"name": "urban", "confidence": 0.85}
            ],
            "description": {
                "tags": ["building", "skyscraper", "city", "architecture", "outdoor"],
                "captions": [{"text": "an aerial view of the Empire State Building in New York City", "confidence": 0.94}]
            },
            "categories": [
                {"name": "building_", "score": 0.95},
                {"name": "outdoor_", "score": 0.75}
            ],
            "imageType": {"clipArtType": 0, "lineDrawingType": 0},
            "color": {
                "dominantColorForeground": "Grey",
                "dominantColorBackground": "Blue",
                "dominantColors": ["Grey", "Blue", "White"],
                "accentColor": "8C7B6E",
                "isBwImg": False
            }
        }
    
    def _preview_vision_vectorize(self, image_url: str) -> Dict:
        """Official output: vector (1024 dimensions for Azure AI Vision multimodal embeddings)"""
        return {
            "id": "doc_001",
            "content": f"[Image: {image_url.split('/')[-1]}]",
            "imageVector": [
                0.0123, -0.0456, 0.0789, -0.0234, 0.0567, -0.0891, 0.0345, -0.0678,
                0.0912, -0.0147, 0.0258, -0.0369, 0.0471, -0.0582, 0.0693, -0.0804,
                "...(1024 dimensions total - Azure AI Vision 4.0 multimodal embeddings)"
            ]
        }
    
    def _preview_document_extraction(self, image_url: str) -> Dict:
        """Official output: content, normalized_images - extracts content from documents"""
        return {
            "id": "doc_001",
            "content": f"[Document: {image_url.split('/')[-1]}]",
            "extractedContent": """CONTOSO LTD.
INVOICE

Invoice Number: INV-100
Invoice Date: November 15, 2019
Invoice Due Date: December 15, 2019

From: Contoso Consulting Ltd, 123 456th St, New York, NY 10001
To: Microsoft Finance Department, 1020 Enterprise Way, Sunnyville, CA 87659

Service Period: 11/4/2019 - 11/15/2019
Consultant: John Smith
Total Hours: 10
Rate: $10.00/hr
Amount Due: $110.00""",
            "normalized_images": [
                {
                    "imageStoreUri": "/document-extraction/normalized/img_001.png",
                    "width": 2200,
                    "height": 1700,
                    "originalWidth": 2200,
                    "originalHeight": 1700,
                    "rotationFromOriginal": 0,
                    "contentOffset": 0,
                    "pageNumber": 1
                }
            ]
        }
    
    def _preview_doc_intelligence(self, image_url: str) -> Dict:
        """Official output: markdown_document (structured markdown with layout info)"""
        return {
            "id": "doc_001",
            "content": f"[Document: {image_url.split('/')[-1]}]",
            "markdown_document": """# CONTOSO LTD.

## INVOICE

| Field | Value |
|-------|-------|
| Invoice Number | INV-100 |
| Invoice Date | November 15, 2019 |
| Invoice Due Date | December 15, 2019 |
| Charges | $110.00 |
| VAT ID | GB123456789 |

### From:
**Contoso Consulting Ltd**  
123 456th St  
New York, NY 10001

### To:
**Microsoft Finance Department**  
1020 Enterprise Way  
Sunnyville, CA 87659

### Service Details

| Period | Consultant | Hours | Rate | Amount |
|--------|-----------|-------|------|--------|
| 11/4/2019 - 11/15/2019 | John Smith | 10 | $10.00/hr | $100.00 |

**Amount Due: $110.00**

---
*Thank you for your business.*"""
        }
    
    def _preview_embedding(self, text: str) -> Dict:
        """Official output: embedding (1536 dimensions for text-embedding-ada-002)"""
        return {
            "id": "doc_001",
            "content": text[:200],
            "contentVector": [-0.006929, -0.005336, 0.004547, -0.027633, 0.025471, "...(1536 dimensions total)"]
        }
    
    def _preview_generic(self, text: str) -> Dict:
        return {"id": "doc_001", "content": text[:200], "output": "[Skill output would appear here]"}
    
    def format_output(self, result: Dict) -> str:
        """Format result for display."""
        return json.dumps(result, indent=2, ensure_ascii=False)
