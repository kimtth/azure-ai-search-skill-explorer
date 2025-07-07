from .baseskill import ImageSkill
from azure.search.documents.indexes.models import (
    OcrSkill, ImageAnalysisSkill, OutputFieldMappingEntry
)


class OcrSkillTest(ImageSkill):
    def __init__(self):
        super().__init__("OcrSkill")
        self.outputs = [
            OutputFieldMappingEntry(name="text", target_name="ocrText")
        ]
    
    def create_skill(self):
        return OcrSkill(
            inputs=self.inputs,
            outputs=self.outputs
        )
    
    def get_sample_input(self) -> bytes:
        from PIL import Image, ImageDraw, ImageFont
        from io import BytesIO
        
        img = Image.new('RGB', (400, 200), color='white')
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype("arial.ttf", 40)
        except:
            font = ImageFont.load_default()
        
        draw.text((50, 50), "OCR TEST TEXT", fill='black', font=font)
        draw.text((50, 100), "Azure AI Search", fill='blue', font=font)
        
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        return buffer.getvalue()


class ImageAnalysisSkillTest(ImageSkill):
    def __init__(self):
        super().__init__("ImageAnalysisSkill")
        self.outputs = [
            OutputFieldMappingEntry(name="tags", target_name="imageTags"),
            OutputFieldMappingEntry(name="description", target_name="imageDescription")
        ]
    
    def create_skill(self):
        return ImageAnalysisSkill(
            inputs=self.inputs,
            outputs=self.outputs,
            visual_features=["Tags", "Description"]
        )
    
    def get_sample_input(self) -> bytes:
        from PIL import Image, ImageDraw
        from io import BytesIO
        
        # Create a simple geometric image
        img = Image.new('RGB', (300, 300), color='white')
        draw = ImageDraw.Draw(img)
        
        # Draw shapes
        draw.rectangle([50, 50, 150, 150], fill='red', outline='black')
        draw.ellipse([150, 150, 250, 250], fill='blue', outline='black')
        
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        return buffer.getvalue()
