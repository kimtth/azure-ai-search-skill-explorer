"""Sample data for Azure AI Search skill demonstrations."""

import os

# Sample text for text-based skills - Wikipedia excerpt about Azure
TEXT_SAMPLE = """Azure AI Search (formerly known as Azure Cognitive Search) is a cloud search service 
that gives developers infrastructure, APIs, and tools for building a rich search experience over 
private, heterogeneous content in web, mobile, and enterprise applications.

Microsoft Azure was announced in October 2008 and released on February 1, 2010. The platform 
supports many different programming languages, tools, and frameworks, including both Microsoft-specific 
and third-party software and systems.

John Smith, the CEO of Contoso Ltd, announced the partnership on January 15, 2024. He can be reached 
at john.smith@contoso.com or by phone at +1-425-555-0123. The company headquarters is located at 
One Microsoft Way, Redmond, WA 98052, United States.

Azure provides more than 200 products and cloud services designed to help bring new solutions to life. 
The sentiment about cloud adoption has been overwhelmingly positive, with enterprises reporting 
significant cost savings and improved scalability."""

# Sample text in different languages for language detection and translation
MULTILINGUAL_SAMPLES = {
    "en": "Azure AI Search is a powerful cloud-based search service from Microsoft.",
    "es": "Azure AI Search es un potente servicio de búsqueda basado en la nube de Microsoft.",
    "fr": "Azure AI Search est un puissant service de recherche basé sur le cloud de Microsoft.",
    "de": "Azure AI Search ist ein leistungsstarker cloudbasierter Suchdienst von Microsoft.",
    "ja": "Azure AI Searchは、マイクロソフトの強力なクラウドベースの検索サービスです。",
    "zh": "Azure AI Search 是微软强大的云搜索服务。",
}

# Sample text with PII for PII detection skill
PII_SAMPLE = """Customer Record:
Name: Sarah Johnson
Email: sarah.johnson@example.com
Phone: +1-206-555-0198
SSN: 123-45-6789
Credit Card: 4532-1234-5678-9012
Address: 456 Pine Street, Seattle, WA 98101
Date of Birth: March 15, 1985
IP Address: 192.168.1.100
Driver's License: WA-SMITH-123456"""

# Sample text for sentiment analysis
SENTIMENT_SAMPLES = {
    "positive": "I absolutely love this product! It exceeded all my expectations and the customer service was fantastic.",
    "negative": "This was a terrible experience. The product broke after one day and customer support was unhelpful.",
    "neutral": "The package arrived on Tuesday. It contained the items as described in the order confirmation.",
    "mixed": "The product quality is excellent, but the delivery took much longer than expected."
}

# Sample text for entity recognition
ENTITY_SAMPLE = """Microsoft Corporation, headquartered in Redmond, Washington, announced today that CEO 
Satya Nadella will present at the upcoming technology conference in San Francisco on December 15, 2024. 
The event will feature demonstrations of Azure AI services and the latest advances in artificial intelligence.

Apple Inc. and Google LLC are also expected to participate. The conference venue, Moscone Center, 
can accommodate 10,000 attendees. Registration fees start at $500 for early bird tickets."""

# Sample image paths for image-based skills (local files)
IMAGE_SAMPLES = {
    "invoice": {
        "path": os.path.join(os.path.dirname(__file__), "..", "samples", "invoice.jpg"),
        "description": "Sample invoice document for OCR demonstration",
    },
    "landscape": {
        "path": os.path.join(os.path.dirname(__file__), "..", "samples", "landscape.jpg"),
        "description": "Sample landscape image for image analysis",
    },
}

# Sample text for text splitting skill
LONG_TEXT_SAMPLE = """Chapter 1: Introduction to Cloud Computing

Cloud computing has revolutionized the way organizations approach their IT infrastructure. 
Instead of maintaining expensive on-premises servers, businesses can now leverage scalable 
resources from cloud providers like Microsoft Azure, Amazon Web Services, and Google Cloud Platform.

Chapter 2: Azure AI Services

Microsoft Azure offers a comprehensive suite of AI services that enable developers to build 
intelligent applications. Azure AI Search provides powerful search capabilities, while Azure 
Cognitive Services offers pre-built AI models for vision, speech, language, and decision-making.

Chapter 3: Building Search Solutions

When building search solutions with Azure AI Search, developers can leverage built-in skills 
to enrich their content. These skills include OCR for extracting text from images, key phrase 
extraction for identifying important terms, and entity recognition for detecting people, places, 
and organizations.

Chapter 4: Best Practices

Effective search solutions require careful planning of the index schema, skillset configuration, 
and query design. Performance optimization and cost management are also critical considerations 
for production deployments."""


def _get_image_path(image_key: str) -> str:
    """Get absolute file path for image."""
    path = IMAGE_SAMPLES[image_key]["path"]
    return os.path.abspath(path)


def get_sample_for_skill(skill_name: str) -> str:
    """Return appropriate sample data based on skill type."""
    skill_samples = {
        "LanguageDetectionSkill": MULTILINGUAL_SAMPLES["en"],
        "KeyPhraseExtractionSkill": TEXT_SAMPLE,
        "EntityRecognitionSkill": ENTITY_SAMPLE,
        "SentimentSkill": SENTIMENT_SAMPLES["mixed"],
        "PIIDetectionSkill": PII_SAMPLE,
        "TextTranslationSkill": MULTILINGUAL_SAMPLES["en"],
        "EntityLinkingSkill": ENTITY_SAMPLE,
        "SplitSkill": LONG_TEXT_SAMPLE,
        "MergeSkill": TEXT_SAMPLE,
        "ShaperSkill": TEXT_SAMPLE,
        "ConditionalSkill": TEXT_SAMPLE,
        "AzureOpenAIEmbeddingSkill": TEXT_SAMPLE,
        # Image-based skills - return file paths
        "OcrSkill": _get_image_path("invoice"),
        "ImageAnalysisSkill": _get_image_path("landscape"),
        "VisionVectorizeSkill": _get_image_path("landscape"),
        "DocumentExtractionSkill": _get_image_path("invoice"),
        "DocumentIntelligenceLayoutSkill": _get_image_path("invoice"),
    }
    return skill_samples.get(skill_name, TEXT_SAMPLE)


def is_image_skill(skill_name: str) -> bool:
    """Check if skill requires image input."""
    return skill_name in ("OcrSkill", "ImageAnalysisSkill", "VisionVectorizeSkill",
                          "DocumentExtractionSkill", "DocumentIntelligenceLayoutSkill")


def get_image_samples() -> dict:
    """Return all available image samples."""
    return IMAGE_SAMPLES
