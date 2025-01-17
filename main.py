from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
import sys
<<<<<<< HEAD
from PyQt6.QtWidgets import QPushButton
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton
import sys
from IPChecker import IPChecker
from DomainChecker import DomainChecker
# 
class MainWindow(QMainWindow):
=======
from PyQt6.QtWidgets import QFileDialog, QPushButton, QTextEdit, QHBoxLayout
import os
# DOMAINS HERE
# Load the .env file manually
from pathlib import Path
env_path = Path('.env')
if env_path.exists():
    # // d
    with open(env_path) as f
        for line in f:
            if line.startswith("API_KEY"):
                API_KEY = line.strip().split('=')[1]

# Define the static column order
STATIC_HEADERS = [
    "country_flag", "ip", "organization", "isp", "country_name_official", "country_capital", 
    "city", "district", "country_name", "connection_type", "zipcode", "longitude", 
    "latitude", "country_tld", "languages", "time_zone", "calling_code"
]
class IPTable(QMainWindow):
>>>>>>> 94160f9 (1 commit)
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bulk Checking Tool")
        self.setGeometry(100, 100, 400, 200)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        
        self.ipCheckerButton = QPushButton("IP Checker")
        self.ipCheckerButton.clicked.connect(self.open_ip_checker)
        self.domainCheckerButton = QPushButton("Domain Checker")
        self.domainCheckerButton.clicked.connect(self.open_domain_checker)
        
        layout.addWidget(self.ipCheckerButton)
        layout.addWidget(self.domainCheckerButton)
        
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def open_ip_checker(self):
        self.ip_checker = IPChecker()
        self.ip_checker.show()

    def open_domain_checker(self):
        self.domain_checker = DomainChecker()
        self.domain_checker.show()

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
