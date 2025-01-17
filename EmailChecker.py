import re
import requests
import tldextract
import tkinter as tk
from tkinter import messagebox, filedialog
import csv

class EmailChecker:
    def __init__(self, api_key):
        self.api_key = api_key

    def is_valid_email(self, email):
        """
        Validates the email address using a regular expression.
        :param email: str
        :return: bool
        """
        email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        return re.match(email_regex, email) is not None

    def get_domain_info(self, email):
        """
        Extracts the domain from the email and fetches location data.
        :param email: str
        :return: str
        """
        # Extract the domain from the email address
        domain = tldextract.extract(email).registered_domain
        # Make a request to the IP info service to get location data
        response = requests.get(f"https://ipinfo.io/{domain}/json")
        if response.status_code == 200:
            data = response.json()
            location = data.get("country", "Unknown")
            return domain, location
        return domain, "Unknown"

    def fetch_and_display_data(self, ips):
        """
        Fetches geolocation data for a list of IP addresses.
        :param ips: list of str
        :return: list of dict
        """
        data = []
        for ip in ips:
            url = "https://api.ipgeolocation.io/ipgeo?apiKey=" + self.api_key + "&ip=" + ip
            response = requests.get(url)
            if response.status_code == 200:
                data.append(response.json())
            else:
                data.append({"ip": ip, "error": "Unable to fetch data"})
        return data

    def check_emails(self, emails):
        """
        Checks if the entered emails are valid and displays domain and location info.
        :param emails: list of str
        """
        results = []
        for email in emails:
            if self.is_valid_email(email):
                domain, location = self.get_domain_info(email)
                results.append(f"Valid Email Address\nDomain: {domain}\nLocation: {location}")
            else:
                results.append("Invalid Email Address")
        messagebox.showinfo("Results", "\n\n".join(results))

    def check_email(self):
        """
        Checks the email entered in the entry widget.
        """
        email = email_entry.get()
        self.check_emails([email])

    def load_emails_from_csv(self):
        """
        Loads emails from a CSV file and checks them.
        """
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            with open(file_path, newline='') as csvfile:
                reader = csv.reader(csvfile)
                emails = [row[0] for row in reader]
                self.check_emails(emails)

# Create the main window
root = tk.Tk()
root.title("Email Checker")

# Create an instance of EmailChecker
email_checker = EmailChecker(api_key='your_api_key_here')

# Create and place the widgets
tk.Label(root, text="Enter Email:").grid(row=0, column=0, padx=10, pady=10)
email_entry = tk.Entry(root, width=30)
email_entry.grid(row=0, column=1, padx=10, pady=10)

check_button = tk.Button(root, text="Check", command=email_checker.check_email)
check_button.grid(row=1, column=0, columnspan=2, pady=10)

load_csv_button = tk.Button(root, text="Load from CSV", command=email_checker.load_emails_from_csv)
load_csv_button.grid(row=2, column=0, columnspan=2, pady=10)

# Run the application
root.mainloop()