from markitdown import MarkItDown
from .baseparser import BaseParser


class MarkitdownParser(BaseParser):
    def __init__(self):
        self.markitdown = MarkItDown(enable_plugins=False)
    
    def parse_by_filepath(self, file_path: str) -> dict:
        """Parse a file using MarkItDown and return the result as a dictionary."""
        try:
            result = self.markitdown.convert(file_path)
            return {
                "text_content": result.text_content,
                "title": getattr(result, 'title', None),
                "success": True,
                "error": None
            }
        except Exception as e:
            return {
                "text_content": None,
                "title": None,
                "success": False,
                "error": str(e)
            }
