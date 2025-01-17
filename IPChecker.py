import csv
import requests
from PyQt6.QtWidgets import QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QLabel, QFileDialog, QPushButton, QTextEdit, QHBoxLayout
from PyQt6.QtGui import QPixmap
from pathlib import Path

# Load the .env file manually
env_path = Path('.env')
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            if line.startswith("API_KEY"):
                API_KEY = line.strip().split('=')[1]

# Define the static column order
STATIC_HEADERS = [
    "country_flag", "ip", "organization", "isp", "country_name_official", "country_capital", 
    "city", "district", "country_name", "connection_type", "zipcode", "longitude", 
    "latitude", "country_tld", "languages", "time_zone", "calling_code"
]

class IPChecker(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("IP Bulk Checking Tool")
        self.setGeometry(100, 100, 800, 600)
        self.data = []
        self.headers = STATIC_HEADERS
        self.initUI()

    def initUI(self):
        self.tableWidget = QTableWidget()
        self.tableWidget.setSortingEnabled(True)
        layout = QVBoxLayout()
        
        # Add buttons and text area for input
        self.importButton = QPushButton("Import CSV")
        self.importButton.clicked.connect(self.import_csv)
        self.pasteButton = QPushButton("Paste IPs")
        self.pasteButton.clicked.connect(self.paste_ips)
        self.textEdit = QTextEdit()
        
        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(self.importButton)
        buttonLayout.addWidget(self.pasteButton)
        
        layout.addLayout(buttonLayout)
        layout.addWidget(self.textEdit)
        layout.addWidget(self.tableWidget)
        
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def import_csv(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Open CSV", "", "CSV Files (*.csv)")
        if file_path:
            with open(file_path, mode='r', encoding='utf-8') as csv_file:
                csv_reader = csv.reader(csv_file)
                ips = [row[0] for row in csv_reader if row]
                self.fetch_and_display_data(ips)

    def paste_ips(self):
        ip_text = self.textEdit.toPlainText()
        ips = [ip.strip() for ip in ip_text.split('\n') if ip.strip()]
        self.fetch_and_display_data(ips)

    def fetch_and_display_data(self, ips):
        self.data = []
        for ip in ips:
            url = "https://api.ipgeolocation.io/ipgeo?apiKey=" + API_KEY + "&ip=" + ip
            response = requests.get(url)
            data = response.json()
            self.data.append(data)
        
        self.tableWidget.setRowCount(len(self.data))
        self.tableWidget.setColumnCount(len(self.headers))
        self.tableWidget.setHorizontalHeaderLabels(self.headers)
        
        for row_idx, row_data in enumerate(self.data):
            for col_idx, header in enumerate(self.headers):
                if header == "country_flag":
                    label = QLabel()
                    pixmap = QPixmap()
                    pixmap.loadFromData(requests.get(row_data[header]).content)
                    label.setPixmap(pixmap)
                    self.tableWidget.setCellWidget(row_idx, col_idx, label)
                else:
                    self.tableWidget.setItem(row_idx, col_idx, QTableWidgetItem(str(row_data.get(header, ""))))
