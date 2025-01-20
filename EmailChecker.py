import re
import requests
import tldextract
import csv
from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QLabel, QFileDialog, QPushButton, QTextEdit, QHBoxLayout, QTableWidget, QTableWidgetItem, QApplication

class EmailChecker(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Email Bulk Checking Tool")
        self.setGeometry(100, 100, 800, 600)
        self.initUI()

    def initUI(self):
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
        
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def is_valid_email(self, email):
        email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        return re.match(email_regex, email) is not None

    def get_domain_info(self, email):
        domain = tldextract.extract(email).registered_domain
        response = requests.get(f"https://ipinfo.io/{domain}/json")
        if response.status_code == 200:
            data = response.json()
            location = data.get("country", "Unknown")
            return domain, location
        return domain, "Unknown"

    def import_csv(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Open CSV", "", "CSV Files (*.csv)")
        if file_path:
            with open(file_path, newline='') as csvfile:
                reader = csv.reader(csvfile)
                emails = [row[0] for row in reader]
                self.fetch_and_display_data(emails)

    def paste_emails(self):
        email_text = self.textEdit.toPlainText()
        emails = [email.strip() for email in email_text.split('\n') if email.strip()]
        self.fetch_and_display_data(emails)

    def fetch_and_display_data(self, emails):
        self.data = []
        for email in emails:
            if self.is_valid_email(email):
                domain, location = self.get_domain_info(email)
                self.data.append({"email": email, "domain": domain, "location": location})
            else:
                self.data.append({"email": email, "error": "Invalid Email Address"})
        
        self.tableWidget.setRowCount(len(self.data))
        self.tableWidget.setColumnCount(3)
        self.tableWidget.setHorizontalHeaderLabels(["Email", "Domain", "Location"])
        
        for row_idx, row_data in enumerate(self.data):
            self.tableWidget.setItem(row_idx, 0, QTableWidgetItem(row_data.get("email", "")))
            self.tableWidget.setItem(row_idx, 1, QTableWidgetItem(row_data.get("domain", "")))
            self.tableWidget.setItem(row_idx, 2, QTableWidgetItem(row_data.get("location", row_data.get("error", ""))))

    def export_csv(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getSaveFileName(self, "Save CSV", "", "CSV Files (*.csv)")
        if file_path:
            with open(file_path, mode='w', newline='', encoding='utf-8') as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow(["Email", "Domain", "Location"])
                for row_data in self.data:
                    writer.writerow([row_data.get("email", ""), row_data.get("domain", ""), row_data.get("location", row_data.get("error", ""))])

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