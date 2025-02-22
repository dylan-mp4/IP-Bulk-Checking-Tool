import csv
import requests
from PyQt6.QtWidgets import QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QLabel, QFileDialog, QPushButton, QTextEdit, QHBoxLayout, QTabWidget, QApplication
from PyQt6.QtGui import QPixmap
from PyQt6.QtWebEngineWidgets import QWebEngineView
from pathlib import Path
import folium
import io

# Load the .env file manually
env_path = Path('.env')
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            if line.startswith("IP_API_KEY"):
                try:
                    IP_API_KEY = line.strip().split('=')[1]
                except IndexError:
                    raise ValueError("IP_API_KEY is missing in the .env file")

# Define the static column order
STATIC_HEADERS = [
    "country_flag", "ip", "organization", "isp", "country_name_official", "country_capital", 
    "city", "country_name", "zipcode", "longitude", 
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
        self.tabs = QTabWidget()
        
        self.tableTab = QWidget()
        self.mapTab = QWidget()
        
        self.tabs.addTab(self.tableTab, "Table View")
        self.tabs.addTab(self.mapTab, "Map View")
        
        self.initTableTab()
        self.initMapTab()
        
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
        self.pasteButton = QPushButton("Submit IPs")
        self.pasteButton.clicked.connect(self.paste_ips)
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

    def initMapTab(self):
        layout = QVBoxLayout()
        self.mapView = QWebEngineView()
        layout.addWidget(self.mapView)
        self.mapTab.setLayout(layout)

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
            url = "https://api.ipgeolocation.io/ipgeo?apiKey=" + IP_API_KEY + "&ip=" + ip
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
        
        self.update_map_view()

    def update_map_view(self):
        map_ = folium.Map(location=[0, 0], zoom_start=2)
        for row_data in self.data:
            latitude = row_data.get("latitude")
            longitude = row_data.get("longitude")
            if latitude and longitude:
                folium.Marker([latitude, longitude], popup=row_data.get("ip")).add_to(map_)
        
        data = io.BytesIO()
        map_.save(data, close_file=False)
        self.mapView.setHtml(data.getvalue().decode())

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
