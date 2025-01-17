from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QLabel, QLineEdit, QPushButton, QMessageBox, QTextEdit
from pathlib import Path

class SettingsWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Settings")
        self.setGeometry(100, 100, 400, 300)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.envTextEdit = QTextEdit()
        self.load_env_file()

        self.saveButton = QPushButton("Save")
        self.saveButton.clicked.connect(self.save_env_file)

        layout.addWidget(self.envTextEdit)
        layout.addWidget(self.saveButton)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def load_env_file(self):
        env_path = Path('.env')
        if env_path.exists():
            with open(env_path) as f:
                self.envTextEdit.setText(f.read())

    def save_env_file(self):
        env_content = self.envTextEdit.toPlainText()
        env_path = Path('.env')
        with open(env_path, 'w') as f:
            f.write(env_content)
        QMessageBox.information(self, "Success", ".env file saved successfully.")
