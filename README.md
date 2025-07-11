# Azure AI Search Built-in Skill Explorer

### Azure AI Search Python SDK

- [API Documentation](https://learn.microsoft.com/en-us/python/api/overview/azure/search-documents-readme?view=azure-python)
- [Release History](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/CHANGELOG.md): To install preview versions.

### Skillset

Configure `outputFieldMappings`:

The field should match the output name in the skillset.

- [Skillset concepts in Azure AI Search](https://learn.microsoft.com/en-us/azure/search/cognitive-search-working-with-skillsets)
- [Rest API](https://learn.microsoft.com/en-us/rest/api/searchservice/skillsets)
- [Skills Input & Output](https://learn.microsoft.com/en-us/azure/search/cognitive-search-predefined-skills): See the sections under this link.
- [Skills for extra processing during indexing](https://learn.microsoft.com/en-us/azure/search/cognitive-search-predefined-skills): Skills list.
- [Skill dependencies](https://learn.microsoft.com/en-us/azure/search/cognitive-search-working-with-skillsets#skill-dependencies)

```json
// The fieldMappings is for verbatim data—no enrichment or transformation involved. Basic indexing. Rename or retype fields.
"fieldMappings" : [
  {
    "sourceFieldName" : "SourceKey",
    "targetFieldName" : "IndexKey",
    "mappingFunction" : {
      "name" : "urlEncode"
    }
  }
]
```

For the above output in the skillset, you need to provide outputFieldMappings like this:

```json
// The outputFieldMappings is for in-memory enriched data - you’re persisting the results of AI processing. Skillsets / AI enrichment.
"outputFieldMappings": [
    {
      "sourceFieldName": "/document/parsedDate", # output of skillset
      "targetFieldName": "parsedDate" # Target index field name
    }
  ]
```

#### 🔍 **Path Expression Rules in Azure AI Search**

The **`source`** field in `InputFieldMappingEntry` uses a **path expression** to specify where the input data for a skill should come from. These path expressions follow a **custom JSON-like syntax** defined by Azure AI Search, not a formal standard like XPath or JSONPath.  

✅ **Basic Structure**: `source="/document"` → top-level field reference  
✅ **Nested Fields**: `source="/document/address/city"` → access nested field in structured data  
✅ **Arrays and Wildcards**: `source="/document/pages/*/content"` → iterate over array to extract page content. The * is a wildcard that represents array.  
✅ **Skill Output Paths**: `source="/document/pages/*/entities"` → skill output path for recognized entities  
✅ **Source Context**: `sourceContext="/document/pages/*"` → set base path for recursive skill inputs  

### UI

![main_ui](doc/main_ui.png)


