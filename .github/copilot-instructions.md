# Azure AI Search Skill Explorer - Copilot Instructions

## Project Overview

This is a **PyQt6 desktop application** for previewing Azure AI Search built-in skill outputs. It shows how skill outputs would appear when stored in an Azure AI Search index—using official Azure output schemas. Supports both local preview and real Azure AI Search index creation/querying.

**Languages & Frameworks:** Python 3.12+, PyQt6  
**Key Dependencies:** `PyQt6`, `python-dotenv`, `azure-search-documents`

---

## Repository Structure

```
├── main_window.py              # PyQt6 main window with Azure connection UI
├── pyproject.toml              # Poetry project config & dependencies
├── .env.example                # Environment variables template
├── samples/                    # Sample images (invoice.jpg, landscape.jpg)
├── controller/
│   ├── skill_preview.py        # Skill preview engine (official Azure output schemas)
│   └── search_client.py        # Azure AI Search client for index operations
└── skill/
    ├── __init__.py             # Package exports
    └── sample_data.py          # Sample data for each skill type
```

---

## Build & Run

1. **Install dependencies** (requires [Poetry](https://python-poetry.org/)):
   ```bash
   poetry install
   ```
2. **Configure Azure (optional)**:
   ```bash
   cp .env.example .env
   # Edit .env with your Azure AI Search endpoint and API key
   ```
3. **Run the application**:
   ```bash
   poetry run python main_window.py
   ```

---

## Features

### Local Preview
- Select a skill and view expected output format based on official Azure schemas
- Text-based skills use sample text data
- Image-based skills (OCR, ImageAnalysis, VisionVectorize) use real sample images
- No Azure resources required

### Azure Integration
- Connect to Azure AI Search with endpoint and admin API key
- Create indexes tailored to each skill's output schema
- Upload sample documents to test real index behavior
- Query indexes and view actual stored results
- Delete test indexes when done

### Sample Images
- `samples/invoice.jpg` - Professional invoice document for OCR and document extraction demos
- `samples/landscape.jpg` - Scenic landscape image for image analysis demonstrations

---

## Adding a New Skill Preview

1. Add sample data for the skill in `skill/sample_data.py` and update `get_sample_for_skill()`.
2. Add a preview handler method in `controller/skill_preview.py` (e.g., `_preview_new_skill`).
3. Register the handler in the `handlers` dict in `preview_skill()`.
4. Register the `@odata.type` in `_get_skill_definition()`.
5. Add the skill name to the combo box in `main_window.py`.

**Important:** Output schemas must match Azure's official documentation exactly. Reference:
- https://learn.microsoft.com/azure/search/cognitive-search-predefined-skills

---

## Output Schema Structure

Preview output follows this structure:
```json
{
  "skillDefinition": {"@odata.type": "#Microsoft.Skills.Text.V3.EntityRecognitionSkill"},
  "sampleInput": {"recordId": "1", "data": {"text": "..."}},
  "indexDocument": {
    "id": "doc_001",
    "content": "...",
    // skill-specific fields (e.g., persons, namedEntities, keyPhrases)
  }
}
```

---

## Key Concepts

### Skill Categories
| Category   | Skills                                                                 |
|------------|------------------------------------------------------------------------|
| Text       | LanguageDetection, KeyPhrase, Entity, Sentiment, PII, Translation      |
| Image      | OCR, ImageAnalysis, VisionVectorize                                    |
| Document   | DocumentExtraction, DocumentIntelligenceLayout                         |
| Utility    | Conditional, Merge, Shaper, Split                                      |
| Embedding  | AzureOpenAIEmbedding                                                   |

### Sample Data
- `TEXT_SAMPLE`: General Azure/Microsoft text with entities, locations, PII
- `PII_SAMPLE`: Text with emails, SSNs, phone numbers, credit cards
- `ENTITY_SAMPLE`: Text with persons, organizations, locations
- `SENTIMENT_SAMPLES`: Positive, negative, neutral, mixed examples

---

## Azure Documentation References

- **Built-in Skills Reference**: https://learn.microsoft.com/en-us/azure/search/cognitive-search-predefined-skills
- **Skillset Concepts**: https://learn.microsoft.com/en-us/azure/search/cognitive-search-working-with-skillsets
- **Skillset REST API**: https://learn.microsoft.com/en-us/rest/api/searchservice/skillsets

---

## Coding Conventions

- Use type hints for function parameters and return types.
- Follow PEP 8 style guidelines.
- Never use bare `except`—always catch specific exceptions.
- Keep code concise and minimal.

---

## Maintenance Reminder

> **As this project evolves, keep this file updated with:**
> - New skills added to the preview engine
> - Changes to sample data structure
> - Updated Azure documentation links

---

## Additional Resources

- GitHub Copilot Custom Instructions: https://docs.github.com/en/copilot/customizing-copilot/adding-repository-custom-instructions-for-github-copilot
- Azure AI Search Pricing: https://azure.microsoft.com/pricing/details/search/