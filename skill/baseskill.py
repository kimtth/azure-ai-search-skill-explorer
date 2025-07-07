from abc import ABC, abstractmethod
from typing import Dict, List, Union, Optional, Any
from azure.search.documents.indexes.models import (
    InputFieldMappingEntry, OutputFieldMappingEntry
)

class BaseSkill(ABC):
    """Base class for all Azure AI Search skill tests."""
    
    def __init__(self, skill_name: str):
        self.skill_name = skill_name
        self.skill_instance = None
        self.inputs = []
        self.outputs = []
        self.context = "/document"
        self.requires_cognitive_services = True
        self.requires_image_processing = False
        self.has_vector_output = False
        self.vector_dimensions = None
        
    @abstractmethod
    def create_skill(self) -> Any:
        """Create and return the skill instance."""
        pass
    
    @abstractmethod
    def get_sample_input(self) -> Union[str, bytes]:
        """Get sample input data for testing."""
        pass
    
    def get_input_mappings(self) -> List[InputFieldMappingEntry]:
        """Get input field mappings for the skill."""
        return self.inputs
    
    def get_output_mappings(self) -> List[OutputFieldMappingEntry]:
        """Get output field mappings for the skill."""
        return self.outputs
    
    def get_output_field_type(self, output_name: str) -> str:
        """Determine the output field type based on the output name."""
        output_lower = output_name.lower()
        
        if self.has_vector_output or any(x in output_lower for x in ["vector", "embedding"]):
            return "vector_output"
        elif any(x in output_lower for x in ["phrases", "entities", "tags", "persons", "organizations", "locations"]):
            return "collection_output"
        else:
            return "string_output"
    
    def validate_results(self, results: List[Dict]) -> bool:
        """Validate the results from the skill execution."""
        if not results:
            print(f"No results returned for {self.skill_name}")
            return False
        
        # Basic validation - check if expected outputs are present
        for result in results:
            for output in self.outputs:
                field_type = self.get_output_field_type(output.target_name)
                if field_type not in result:
                    print(f"Expected output field '{field_type}' not found in results")
                    return False
        
        return True
    
    def format_results(self, results: List[Dict]) -> str:
        """Format results for display."""
        formatted = f"\n=== Results for {self.skill_name} ===\n"
        for i, result in enumerate(results):
            formatted += f"\nDocument {i + 1}:\n"
            for key, value in result.items():
                if key != "id" and value is not None:
                    if isinstance(value, list):
                        formatted += f"  {key}: {', '.join(str(v) for v in value[:5])}"
                        if len(value) > 5:
                            formatted += f"... ({len(value)} total)"
                        formatted += "\n"
                    else:
                        formatted += f"  {key}: {str(value)[:100]}"
                        if len(str(value)) > 100:
                            formatted += "..."
                        formatted += "\n"
        return formatted


class TextSkill(BaseSkill):
    """Base class for text-based skills."""
    
    def __init__(self, skill_name: str):
        super().__init__(skill_name)
        self.inputs = [
            InputFieldMappingEntry(name="text", source="/document/content")
        ]
        
    def get_sample_input(self) -> str:
        """Get sample text input."""
        return "Microsoft was founded by Bill Gates and Paul Allen in Seattle. The company is headquartered in Redmond, Washington. Contact: info@microsoft.com or call 425-882-8080."


class ImageSkill(BaseSkill):
    """Base class for image-based skills."""
    
    def __init__(self, skill_name: str):
        super().__init__(skill_name)
        self.requires_image_processing = True
        self.inputs = [
            InputFieldMappingEntry(name="image", source="/document/normalized_images/*")
        ]
        
    def get_sample_input(self) -> bytes:
        """Get sample image input."""
        from PIL import Image, ImageDraw, ImageFont
        from io import BytesIO
        
        img = Image.new('RGB', (400, 200), color='white')
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype("arial.ttf", 36)
        except:
            font = ImageFont.load_default()
        
        draw.text((50, 80), f"Test for {self.skill_name}", fill='black', font=font)
        
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        return buffer.getvalue()
