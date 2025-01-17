import requests
from PyQt6.QtWidgets import QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QLabel, QFileDialog, QPushButton, QTextEdit, QHBoxLayout, QTabWidget
from pathlib import Path
import csv

# Load the .env file manually
env_path = Path('.env')
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            if line.startswith("DOMAIN_API_KEY"):
                try:
                    DOMAIN_API_KEY = line.strip().split('=')[1]
                except IndexError:
                    raise ValueError("DOMAIN_API_KEY is missing in the .env file")

# Define the static column order
STATIC_HEADERS = [
    "domain_name", "registrar", "creation_date", "expiration_date", "updated_date", 
    "status", "emails", "name_servers", "whois_server", "dnssec"
]

class DomainChecker(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Domain Bulk Checking Tool")
        self.setGeometry(100, 100, 800, 600)
        self.data = []
        self.headers = STATIC_HEADERS
        self.initUI()

    def initUI(self):
        self.tabs = QTabWidget()
        
        self.tableTab = QWidget()
        
        self.tabs.addTab(self.tableTab, "Table View")
        
        self.initTableTab()
        
        layout = QVBoxLayout()
        layout.addWidget(self.tabs)
        
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def initTableTab(self):
        self.tableWidget = QTableWidget()
        self.tableWidget.setSortingEnabled(True)
        layout = QVBoxLayout()
        
        # Add buttons and text area for input
        self.importButton = QPushButton("Import CSV")
        self.importButton.clicked.connect(self.import_csv)
        self.pasteButton = QPushButton("Submit Domains")
        self.pasteButton.clicked.connect(self.paste_domains)
        self.exportButton = QPushButton("Export CSV")
        self.exportButton.clicked.connect(self.export_csv)
        self.textEdit = QTextEdit()
        
        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(self.importButton)
        buttonLayout.addWidget(self.pasteButton)
        buttonLayout.addWidget(self.exportButton)
        
        layout.addLayout(buttonLayout)
        layout.addWidget(self.textEdit)
        layout.addWidget(self.tableWidget)
        
        self.tableTab.setLayout(layout)

    def import_csv(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Open CSV", "", "CSV Files (*.csv)")
        if file_path:
            with open(file_path, mode='r', encoding='utf-8') as csv_file:
                csv_reader = csv.reader(csv_file)
                domains = [row[0] for row in csv_reader if row]
                self.fetch_and_display_data(domains)

    def paste_domains(self):
        domain_text = self.textEdit.toPlainText()
        domains = [domain.strip() for domain in domain_text.split('\n') if domain.strip()]
        self.fetch_and_display_data(domains)

    def fetch_and_display_data(self, domains):
        self.data = []
        for domain in domains:
            url = f"https://api.apilayer.com/whois/query?domain={domain}"
            headers = {"apikey": DOMAIN_API_KEY}
            response = requests.get(url, headers=headers)
            data = response.json().get("result", {})
            self.data.append(data)
        
        self.tableWidget.setRowCount(len(self.data))
        self.tableWidget.setColumnCount(len(self.headers))
        self.tableWidget.setHorizontalHeaderLabels(self.headers)
        
        for row_idx, row_data in enumerate(self.data):
            for col_idx, header in enumerate(self.headers):
                self.tableWidget.setItem(row_idx, col_idx, QTableWidgetItem(str(row_data.get(header, ""))))

    def export_csv(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getSaveFileName(self, "Save CSV", "", "CSV Files (*.csv)")
        if file_path:
            with open(file_path, mode='w', newline='', encoding='utf-8') as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow(self.headers)
                for row_data in self.data:
                    writer.writerow([row_data.get(header, "") for header in self.headers])
