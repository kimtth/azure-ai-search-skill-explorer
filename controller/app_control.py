import os
import threading
import traceback
from typing import Dict, List, Union, Optional
from PyQt6.QtCore import QObject, pyqtSignal
from ..main_window import AzureSearchSkillTester
from skill import *
from parse.markitdown_parser import MarkitdownParser

class AppController(QObject):
    # Signals for UI updates
    progress_updated = pyqtSignal(int)
    log_message = pyqtSignal(str)
    test_completed = pyqtSignal(list)
    error_occurred = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.tester = None
        self.parser = MarkitdownParser()
        self.skill_classes = {
            'CustomEntityLookupSkill': CustomEntityLookupSkillTest,
            'KeyPhraseExtractionSkill': KeyPhraseExtractionSkillTest,
            'LanguageDetectionSkill': LanguageDetectionSkillTest,
            'EntityRecognitionSkill': EntityRecognitionSkillTest,
            'EntityLinkingSkill': EntityLinkingSkillTest,
            'PIIDetectionSkill': PIIDetectionSkillTest,
            'SentimentSkill': SentimentSkillTest,
            'TranslationSkill': TextTranslationSkillTest,
            'ImageAnalysisSkill': ImageAnalysisSkillTest,
            'OcrSkill': OcrSkillTest,
            'VisionVectorizeSkill': VisionVectorizeSkillTest,
            'DocumentIntelligenceLayoutSkill': DocumentIntelligenceLayoutSkillTest,
            'AzureOpenAIEmbeddingSkill': AzureOpenAIEmbeddingSkillTest,
            'ConditionalSkill': ConditionalSkillTest,
            'DocumentExtractionSkill': DocumentExtractionSkillTest,
            'MergeSkill': MergeSkillTest,
            'ShaperSkill': ShaperSkillTest,
            'SplitSkill': SplitSkillTest,
        }
    
    def initialize_tester(self) -> bool:
        """Initialize the Azure Search Skill Tester with environment validation."""
        try:
            # Validate required environment variables
            required_vars = ["SEARCH_SERVICE_NAME", "SEARCH_ADMIN_KEY", "SEARCH_QUERY_KEY", 
                           "COGNITIVE_SERVICES_KEY", "STORAGE_ACCOUNT_NAME", "STORAGE_ACCOUNT_KEY"]
            
            missing_vars = [var for var in required_vars if not os.environ.get(var)]
            if missing_vars:
                self.error_occurred.emit(f"Missing environment variables: {', '.join(missing_vars)}")
                return False
            
            # Initialize the tester
            self.tester = AzureSearchSkillTester()
            self.log_message.emit("✅ Azure Search Skill Tester initialized successfully.")
            return True
            
        except Exception as e:
            self.error_occurred.emit(f"Failed to initialize tester: {str(e)}")
            self.log_message.emit(f"Initialization error details: {traceback.format_exc()}")
            return False
    
    def parse_file(self, file_path: str) -> Optional[str]:
        """Parse a file and return its text content."""
        try:
            self.log_message.emit(f"📄 Parsing file: {os.path.basename(file_path)}")
            result = self.parser.parse_by_filepath(file_path)
            
            if result['success']:
                content_length = len(result['text_content']) if result['text_content'] else 0
                self.log_message.emit(f"✅ File parsed successfully. Content length: {content_length} characters")
                return result['text_content']
            else:
                self.error_occurred.emit(f"Failed to parse file: {result['error']}")
                return None
                
        except Exception as e:
            error_msg = f"Error parsing file: {str(e)}"
            self.error_occurred.emit(error_msg)
            self.log_message.emit(f"Parse error details: {traceback.format_exc()}")
            return None
    
    def run_skill_test(self, file_path: str, skill_name: str):
        """Run skill test in a separate thread."""
        thread = threading.Thread(target=self._execute_skill_test, args=(file_path, skill_name))
        thread.daemon = True
        thread.start()
    
    def _execute_skill_test(self, file_path: str, skill_name: str):
        """Execute the skill test with progress updates."""
        try:
            self.progress_updated.emit(5)
            self.log_message.emit(f"🚀 Starting skill test: {skill_name}")
            
            # Initialize tester if not already done
            if not self.tester:
                self.log_message.emit("🔧 Initializing Azure services...")
                if not self.initialize_tester():
                    self.progress_updated.emit(0)
                    return
            
            self.progress_updated.emit(15)
            
            # Parse file content if provided
            custom_input = None
            if file_path:
                file_ext = os.path.splitext(file_path)[1].lower()
                image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff'}
                
                if file_ext in image_extensions:
                    # Handle image files
                    try:
                        with open(file_path, 'rb') as f:
                            custom_input = f.read()
                        self.log_message.emit(f"🖼️ Image file loaded: {len(custom_input)} bytes")
                    except Exception as e:
                        self.error_occurred.emit(f"Error reading image file: {str(e)}")
                        self.progress_updated.emit(0)
                        return
                else:
                    # Parse text-based files
                    custom_input = self.parse_file(file_path)
                    if custom_input is None:
                        self.progress_updated.emit(0)
                        return
            
            self.progress_updated.emit(30)
            
            # Validate skill name
            if skill_name not in self.skill_classes:
                self.error_occurred.emit(f"Unknown skill: {skill_name}")
                self.progress_updated.emit(0)
                return
            
            skill_class = self.skill_classes[skill_name]
            self.log_message.emit(f"🔍 Executing {skill_name} skill...")
            
            self.progress_updated.emit(50)
            
            # Execute the test
            try:
                results = self.tester.test_skill_with_class(skill_class, custom_input)
                self.progress_updated.emit(85)
                
                # Process and emit results
                if results:
                    skill_test = self._create_skill_instance(skill_class)
                    formatted_results = skill_test.format_results(results)
                    self.log_message.emit("📊 Test completed successfully!")
                    self.log_message.emit(formatted_results)
                    self.test_completed.emit(results)
                else:
                    self.log_message.emit("⚠️ No results returned from skill test")
                    self.test_completed.emit([])
                
            except Exception as skill_error:
                error_msg = f"Skill execution failed: {str(skill_error)}"
                self.error_occurred.emit(error_msg)
                self.log_message.emit(f"Skill error details: {traceback.format_exc()}")
                self.progress_updated.emit(0)
                return
            
            self.progress_updated.emit(100)
            self.log_message.emit(f"✅ Skill test completed: {skill_name}")
            
        except Exception as e:
            error_msg = f"Unexpected error during skill test: {str(e)}"
            self.error_occurred.emit(error_msg)
            self.log_message.emit(f"Unexpected error details: {traceback.format_exc()}")
            self.progress_updated.emit(0)
    
    def _create_skill_instance(self, skill_class):
        """Create skill instance with proper parameters."""
        try:
            if skill_class == AzureOpenAIEmbeddingSkillTest:
                return skill_class(
                    self.tester.aoai_resource_uri,
                    self.tester.aoai_deployment_id,
                    self.tester.embedding_dimensions
                )
            else:
                return skill_class()
        except Exception as e:
            self.log_message.emit(f"Warning: Could not create skill instance: {str(e)}")
            # Return a basic instance for fallback
            return skill_class()
