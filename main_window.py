import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QProgressBar, QTextEdit, QHBoxLayout, QFileDialog, QSizePolicy, QComboBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

# Import the tester and skill classes directly
from controller.skill_tester import AzureSearchSkillTester
from skill import (
    LanguageDetectionSkillTest, KeyPhraseExtractionSkillTest,
    EntityRecognitionSkillTest, SentimentSkillTest, PIIDetectionSkillTest,
    TextTranslationSkillTest, EntityLinkingSkillTest, CustomEntityLookupSkillTest,
    VectorizeSkillTest, OcrSkillTest, ImageAnalysisSkillTest,
    DocumentExtractionSkillTest, DocumentIntelligenceLayoutSkillTest,
    ConditionalSkillTest, MergeSkillTest, ShaperSkillTest, SplitSkillTest,
    AzureOpenAIEmbeddingSkillTest
)

class AzureAISkillExplorer(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        # instantiate the tester
        self.tester = AzureSearchSkillTester()
        # map display names to test classes
        self.skill_map = {
            'LanguageDetectionSkill': LanguageDetectionSkillTest,
            'KeyPhraseExtractionSkill': KeyPhraseExtractionSkillTest,
            'EntityRecognitionSkill': EntityRecognitionSkillTest,
            'SentimentSkill': SentimentSkillTest,
            'PIIDetectionSkill': PIIDetectionSkillTest,
            'TranslationSkill': TextTranslationSkillTest,
            'EntityLinkingSkill': EntityLinkingSkillTest,
            'CustomEntityLookupSkill': CustomEntityLookupSkillTest,
            'VectorizeSkill': VectorizeSkillTest,
            'OcrSkill': OcrSkillTest,
            'ImageAnalysisSkill': ImageAnalysisSkillTest,
            'DocumentExtractionSkill': DocumentExtractionSkillTest,
            'DocumentIntelligenceLayoutSkill': DocumentIntelligenceLayoutSkillTest,
            'ConditionalSkill': ConditionalSkillTest,
            'MergeSkill': MergeSkillTest,
            'ShaperSkill': ShaperSkillTest,
            'SplitSkill': SplitSkillTest,
            'AzureOpenAIEmbeddingSkill': AzureOpenAIEmbeddingSkillTest
        }

    def initUI(self):
        self.setWindowTitle('Azure AI Search Skill Explorer')
        self.setGeometry(100, 100, 600, 500)
        self.setFixedSize(600, 500)  # Set fixed window size
        self.setWindowIcon(QIcon('azure.png'))  # Set custom icon

        layout = QVBoxLayout()

        # Header Label
        header = QLabel('Azure AI Search Skill Explorer')
        header.setStyleSheet('background-color: #0066b3; color: white; padding: 10px; font-size: 16px;')
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)

        # Blob file input section
        file_layout = QHBoxLayout()
        file_label = QLabel('Blob file')
        file_label.setFixedWidth(80)
        self.file_input = QLineEdit()
        browse_button = QPushButton('Browse')
        browse_button.clicked.connect(self.browseFile)

        file_layout.addWidget(file_label)
        file_layout.addWidget(self.file_input)
        file_layout.addWidget(browse_button)

        layout.addLayout(file_layout)

        # Skill select dropdown
        skill_layout = QHBoxLayout()
        skill_label = QLabel('Skill')
        skill_label.setFixedWidth(80)
        self.skill_combo = QComboBox()
        self.skill_combo.addItems([
            'CustomEntityLookupSkill',
            'KeyPhraseExtractionSkill',
            'LanguageDetectionSkill',
            'EntityRecognitionSkill',
            'EntityLinkingSkill',
            'PIIDetectionSkill',
            'SentimentSkill',
            'TranslationSkill',
            'ImageAnalysisSkill',
            'OcrSkill',
            'VectorizeSkill',
            'DocumentIntelligenceLayoutSkill',
            'AzureOpenAIEmbeddingSkill',
            'ConditionalSkill',
            'DocumentExtractionSkill',
            'MergeSkill',
            'ShaperSkill',
            'SplitSkill',
            # Custom skills
            # WebApiSkill,
            # AmlSkill	
        ])
        self.skill_combo.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        
        run_button = QPushButton('Run')
        run_button.clicked.connect(self.runSkill)

        skill_layout.addWidget(skill_label)
        skill_layout.addWidget(self.skill_combo)
        skill_layout.addWidget(run_button)

        layout.addLayout(skill_layout)

        # Progress bar with fixed height
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(30)
        self.progress_bar.setFormat('Progress bar %')
        self.progress_bar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.progress_bar.setFixedHeight(30)  # Set fixed height
        layout.addWidget(self.progress_bar)

        layout.addSpacing(10)

        # Log area
        self.log_area = QTextEdit()
        self.log_area.setPlaceholderText('Log area')
        self.log_area.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout.addWidget(self.log_area)

        self.setLayout(layout)

    def browseFile(self):
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        if file_dialog.exec():
            file_path = file_dialog.selectedFiles()[0]
            self.file_input.setText(file_path)

    def runSkill(self):
        """Run the selected skill through the tester and display results."""
        selected = self.skill_combo.currentText()
        cls = self.skill_map.get(selected)
        path = self.file_input.text()
        self.log_area.clear()
        self.progress_bar.setValue(10)

        if not cls:
            self.log_area.append(f"No test class for '{selected}'")
            return

        # call the tester
        results = self.tester.test_skill_with_class(cls, file_path=path)
        self.progress_bar.setValue(100)

        # display results
        for r in results:
            self.log_area.append(str(r))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = AzureAISkillExplorer()
    window.show()
    sys.exit(app.exec())