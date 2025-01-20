import asyncio
import aiohttp
from PyQt6.QtWidgets import QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QLabel, QFileDialog, QPushButton, QTextEdit, QHBoxLayout, QTabWidget, QApplication
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
    "email", "domain_name", "registrar", "creation_date", "expiration_date", "updated_date", 
    "status", "emails", "name_servers", "whois_server", "dnssec"
]

class EmailChecker(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Email Domain Checking Tool")
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
        self.pasteButton = QPushButton("Submit Emails")
        self.pasteButton.clicked.connect(self.paste_emails)
        self.exportButton = QPushButton("Export CSV")
        self.exportButton.clicked.connect(self.export_csv)
        self.copyRowButton = QPushButton("Copy Selected Row")
        self.copyRowButton.clicked.connect(self.copy_selected_row)
        self.copyColumnButton = QPushButton("Copy Selected Column")
        self.copyColumnButton.clicked.connect(self.copy_selected_column)
        self.textEdit = QTextEdit()
        
        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(self.importButton)
        buttonLayout.addWidget(self.pasteButton)
        buttonLayout.addWidget(self.exportButton)
        buttonLayout.addWidget(self.copyRowButton)
        buttonLayout.addWidget(self.copyColumnButton)
        
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
                emails = [row[0] for row in csv_reader if row]
                email_domain_pairs = [(email, email.split('@')[1]) for email in emails if '@' in email]
                self.fetch_and_display_data(email_domain_pairs)

    def paste_emails(self):
        email_text = self.textEdit.toPlainText()
        emails = [email.strip() for email in email_text.split('\n') if email.strip()]
        email_domain_pairs = [(email, email.split('@')[1]) for email in emails if '@' in email]
        self.fetch_and_display_data(email_domain_pairs)

    async def fetch_domain_info(self, session, domain):
        url = f"https://api.apilayer.com/whois/query?domain={domain}"
        headers = {"apikey": DOMAIN_API_KEY}
        async with session.get(url, headers=headers) as response:
            return await response.json()

    async def fetch_and_display_data_async(self, email_domain_pairs):
        async with aiohttp.ClientSession() as session:
            tasks = [self.fetch_domain_info(session, domain) for _, domain in email_domain_pairs]
            results = await asyncio.gather(*tasks)
            self.data = [
                {"email": email, **result.get("result", {})}
                for (email, _), result in zip(email_domain_pairs, results)
                if isinstance(result.get("result", {}), dict)
            ]
        
        self.tableWidget.setRowCount(len(self.data))
        self.tableWidget.setColumnCount(len(self.headers))
        self.tableWidget.setHorizontalHeaderLabels(self.headers)
        
        for row_idx, row_data in enumerate(self.data):
            for col_idx, header in enumerate(self.headers):
                self.tableWidget.setItem(row_idx, col_idx, QTableWidgetItem(str(row_data.get(header, ""))))

    def fetch_and_display_data(self, email_domain_pairs):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.fetch_and_display_data_async(email_domain_pairs))

    def export_csv(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getSaveFileName(self, "Save CSV", "", "CSV Files (*.csv)")
        if file_path:
            with open(file_path, mode='w', newline='', encoding='utf-8') as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow(self.headers)
                for row_data in self.data:
                    writer.writerow([row_data.get(header, "") for header in self.headers])

    def copy_selected_row(self):
        selected_row = self.tableWidget.currentRow()
        if selected_row >= 0:
            row_data = [self.tableWidget.item(selected_row, col).text() for col in range(self.tableWidget.columnCount())]
            clipboard = QApplication.clipboard()
            clipboard.setText("\t".join(row_data))

    def copy_selected_column(self):
        selected_column = self.tableWidget.currentColumn()
        if selected_column >= 0:
            column_data = [self.tableWidget.item(row, selected_column).text() for row in range(self.tableWidget.rowCount())]
            clipboard = QApplication.clipboard()
            clipboard.setText("\n".join(column_data))
