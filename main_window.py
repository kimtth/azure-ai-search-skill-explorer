import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QTextEdit,
    QPushButton, QProgressBar, QHBoxLayout, QSizePolicy, QComboBox,
    QLineEdit, QGroupBox, QTabWidget, QMessageBox,
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from dotenv import load_dotenv
from controller.skill_preview import SkillPreviewEngine
from controller.search_client import AzureSearchClient
from skill.sample_data import get_sample_for_skill, is_image_skill

load_dotenv()


class AzureAISkillExplorer(QWidget):
    def __init__(self):
        super().__init__()
        self.preview_engine = SkillPreviewEngine()
        self.search_client = None
        self.current_index_name = None
        self.worker = None
        self.initUI()
        self._load_config()

    def _load_config(self):
        endpoint = os.getenv("AZURE_SEARCH_ENDPOINT", "")
        api_key = os.getenv("AZURE_SEARCH_API_KEY", "")
        if endpoint:
            self.endpoint_input.setText(endpoint)
        if api_key:
            self.api_key_input.setText(api_key)

    def initUI(self):
        self.setWindowTitle("Azure AI Search Skill Explorer")
        self.setGeometry(100, 100, 800, 700)
        self.setMinimumSize(700, 600)

        layout = QVBoxLayout()

        # Header
        header = QLabel("Azure AI Search Skill Explorer")
        header.setStyleSheet("background-color: #0066b3; color: white; padding: 10px; font-size: 16px;")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)

        # Azure Config Group
        config_group = QGroupBox("Azure AI Search Configuration")
        config_layout = QVBoxLayout()
        
        endpoint_layout = QHBoxLayout()
        endpoint_layout.addWidget(QLabel("Endpoint:"))
        self.endpoint_input = QLineEdit()
        self.endpoint_input.setPlaceholderText("https://your-search-service.search.windows.net")
        endpoint_layout.addWidget(self.endpoint_input)
        config_layout.addLayout(endpoint_layout)
        
        key_layout = QHBoxLayout()
        key_layout.addWidget(QLabel("API Key:"))
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key_input.setPlaceholderText("Enter your admin API key")
        key_layout.addWidget(self.api_key_input)
        config_layout.addLayout(key_layout)
        
        connect_btn = QPushButton("Connect")
        connect_btn.clicked.connect(self.connect_to_azure)
        config_layout.addWidget(connect_btn)
        
        self.connection_status = QLabel("Status: Not connected")
        config_layout.addWidget(self.connection_status)
        
        config_group.setLayout(config_layout)
        layout.addWidget(config_group)

        # Skill selector
        skill_layout = QHBoxLayout()
        skill_label = QLabel("Skill:")
        skill_label.setFixedWidth(50)
        self.skill_combo = QComboBox()
        self.skill_combo.addItems([
            "LanguageDetectionSkill", "KeyPhraseExtractionSkill", "EntityRecognitionSkill",
            "EntityLinkingSkill", "PIIDetectionSkill", "SentimentSkill", "TextTranslationSkill",
            "ImageAnalysisSkill", "OcrSkill", "VisionVectorizeSkill",
            "DocumentExtractionSkill", "DocumentIntelligenceLayoutSkill",
            "ConditionalSkill", "MergeSkill", "ShaperSkill", "SplitSkill",
            "AzureOpenAIEmbeddingSkill",
        ])
        self.skill_combo.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.skill_combo.currentTextChanged.connect(self.on_skill_changed)
        skill_layout.addWidget(skill_label)
        skill_layout.addWidget(self.skill_combo)
        layout.addLayout(skill_layout)

        # Sample input area
        self.input_label = QLabel("Sample Input:")
        layout.addWidget(self.input_label)
        self.input_area = QTextEdit()
        self.input_area.setMaximumHeight(100)
        self.input_area.setPlaceholderText("Sample input text or image URL for the skill...")
        layout.addWidget(self.input_area)

        # Action buttons
        btn_layout = QHBoxLayout()
        self.preview_btn = QPushButton("Preview (Local)")
        self.preview_btn.clicked.connect(self.run_preview)
        btn_layout.addWidget(self.preview_btn)
        
        self.create_index_btn = QPushButton("Create Index & Upload")
        self.create_index_btn.clicked.connect(self.create_index_and_upload)
        self.create_index_btn.setEnabled(False)
        btn_layout.addWidget(self.create_index_btn)
        
        self.query_btn = QPushButton("Query Index")
        self.query_btn.clicked.connect(self.query_index)
        self.query_btn.setEnabled(False)
        btn_layout.addWidget(self.query_btn)
        
        self.delete_btn = QPushButton("Delete Index")
        self.delete_btn.clicked.connect(self.delete_index)
        self.delete_btn.setEnabled(False)
        btn_layout.addWidget(self.delete_btn)
        
        layout.addLayout(btn_layout)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(20)
        layout.addWidget(self.progress_bar)

        # Output tabs
        self.output_tabs = QTabWidget()
        
        self.preview_output = QTextEdit()
        self.preview_output.setReadOnly(True)
        self.output_tabs.addTab(self.preview_output, "Preview Output")
        
        self.index_output = QTextEdit()
        self.index_output.setReadOnly(True)
        self.output_tabs.addTab(self.index_output, "Index Results")
        
        layout.addWidget(self.output_tabs)

        self.setLayout(layout)
        self.on_skill_changed(self.skill_combo.currentText())

    def connect_to_azure(self):
        endpoint = self.endpoint_input.text().strip()
        api_key = self.api_key_input.text().strip()
        
        if not endpoint or not api_key:
            QMessageBox.warning(self, "Error", "Please enter endpoint and API key")
            return
        
        try:
            self.search_client = AzureSearchClient(endpoint, api_key)
            indexes = self.search_client.list_indexes()
            self.connection_status.setText(f"Status: Connected ({len(indexes)} indexes)")
            self.connection_status.setStyleSheet("color: green;")
            self.create_index_btn.setEnabled(True)
            self.query_btn.setEnabled(True)
            self.delete_btn.setEnabled(True)
        except Exception as e:
            self.connection_status.setText(f"Status: Connection failed")
            self.connection_status.setStyleSheet("color: red;")
            QMessageBox.critical(self, "Connection Error", str(e))

    def on_skill_changed(self, skill_name: str):
        sample = get_sample_for_skill(skill_name)
        self.input_area.setPlainText(sample)
        self.preview_output.clear()
        self.progress_bar.setValue(0)
        
        # Update label based on skill type
        if is_image_skill(skill_name):
            self.input_label.setText("Sample Input (Image URL):")
            self.input_area.setPlaceholderText("Enter image URL...")
        else:
            self.input_label.setText("Sample Input (Text):")
            self.input_area.setPlaceholderText("Enter sample text...")

    def run_preview(self):
        self.preview_output.clear()
        self.progress_bar.setValue(20)
        self.output_tabs.setCurrentIndex(0)
        
        skill_name = self.skill_combo.currentText()
        input_text = self.input_area.toPlainText()
        
        self.worker = PreviewWorker(self.preview_engine, skill_name, input_text)
        self.worker.finished.connect(self.on_preview_complete)
        self.worker.start()

    def on_preview_complete(self, result: str):
        self.progress_bar.setValue(100)
        self.preview_output.setPlainText(result)

    def create_index_and_upload(self):
        if not self.search_client:
            return
        
        self.progress_bar.setValue(10)
        skill_name = self.skill_combo.currentText()
        input_text = self.input_area.toPlainText()
        
        self.worker = IndexWorker(
            self.search_client, self.preview_engine, skill_name, input_text, "create"
        )
        self.worker.finished.connect(self.on_index_operation_complete)
        self.worker.start()

    def query_index(self):
        if not self.search_client:
            return
        
        skill_name = self.skill_combo.currentText()
        self.worker = IndexWorker(self.search_client, None, skill_name, "", "query")
        self.worker.finished.connect(self.on_index_operation_complete)
        self.worker.start()

    def delete_index(self):
        if not self.search_client:
            return
        
        skill_name = self.skill_combo.currentText()
        index_name = f"skill-explorer-{skill_name.lower().replace('skill', '')}"
        
        reply = QMessageBox.question(
            self, "Confirm Delete", f"Delete index '{index_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.worker = IndexWorker(self.search_client, None, skill_name, "", "delete")
            self.worker.finished.connect(self.on_index_operation_complete)
            self.worker.start()

    def on_index_operation_complete(self, result: str):
        self.progress_bar.setValue(100)
        self.index_output.setPlainText(result)
        self.output_tabs.setCurrentIndex(1)


class PreviewWorker(QThread):
    finished = pyqtSignal(str)

    def __init__(self, engine: SkillPreviewEngine, skill_name: str, input_text: str):
        super().__init__()
        self.engine = engine
        self.skill_name = skill_name
        self.input_text = input_text

    def run(self):
        result = self.engine.preview_skill(self.skill_name, self.input_text)
        self.finished.emit(self.engine.format_output(result))


class IndexWorker(QThread):
    finished = pyqtSignal(str)

    def __init__(self, client: AzureSearchClient, engine: SkillPreviewEngine, 
                 skill_name: str, input_text: str, operation: str):
        super().__init__()
        self.client = client
        self.engine = engine
        self.skill_name = skill_name
        self.input_text = input_text
        self.operation = operation

    def run(self):
        import json
        try:
            index_name = f"skill-explorer-{self.skill_name.lower().replace('skill', '')}"
            
            if self.operation == "create":
                created_name = self.client.create_skill_index(self.skill_name)
                preview = self.engine.preview_skill(self.skill_name, self.input_text)
                doc = self.client.prepare_document_for_index(self.skill_name, preview["indexDocument"])
                self.client.upload_document(created_name, doc)
                self.finished.emit(f"Index '{created_name}' created and document uploaded.\n\nUploaded document:\n{json.dumps(doc, indent=2)}")
            
            elif self.operation == "query":
                results = self.client.query_index(index_name)
                self.finished.emit(f"Query results from '{index_name}':\n\n{json.dumps(results, indent=2, default=str)}")
            
            elif self.operation == "delete":
                self.client.delete_index(index_name)
                self.finished.emit(f"Index '{index_name}' deleted successfully.")
        
        except Exception as e:
            self.finished.emit(f"Error: {str(e)}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AzureAISkillExplorer()
    window.show()
    sys.exit(app.exec())
