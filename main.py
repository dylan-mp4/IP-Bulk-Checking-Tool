from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton
from PyQt6.QtGui import QAction
import sys
from IPChecker import IPChecker
from DomainChecker import DomainChecker
from EmailChecker import EmailChecker
from SettingsWindow import SettingsWindow

class MainWindow(QMainWindow):
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
        self.emailCheckerButton = QPushButton("Email Checker")
        self.emailCheckerButton.clicked.connect(self.open_email_checker)
        
        layout.addWidget(self.ipCheckerButton)
        layout.addWidget(self.domainCheckerButton)
        layout.addWidget(self.emailCheckerButton)
        
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Add settings action
        settings_action = QAction('Settings', self)
        settings_action.triggered.connect(self.open_settings)
        self.toolbar = self.addToolBar('Settings')
        self.toolbar.addAction(settings_action)
        self.toolbar.setMovable(False)
        self.toolbar.setFloatable(False)


    def open_ip_checker(self):
        self.ip_checker = IPChecker()
        self.ip_checker.show()

    def open_domain_checker(self):
        self.domain_checker = DomainChecker()
        self.domain_checker.show()

    def open_email_checker(self):
        self.email_checker = EmailChecker()
        self.email_checker.show()

    def open_settings(self):
        self.settings_window = SettingsWindow()
        self.settings_window.show()

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
