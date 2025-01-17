import re
import tkinter as tk
from tkinter import messagebox
import tldextract
import requests

def is_valid_email(email):
    """
    Validate the email address using regular expressions.
    :param email: str
    :return: bool
    """
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_regex, email) is not None

def get_domain_info(email):
    """
    Extract the domain from the email and get location info.
    :param email: str
    :return: str
    """
    domain = tldextract.extract(email).registered_domain
    response = requests.get(f"https://ipinfo.io/{domain}/json")
    if response.status_code == 200:
        data = response.json()
        location = data.get("country", "Unknown")
        return domain, location
    return domain, "Unknown"

def check_email():
    email = email_entry.get()
    if is_valid_email(email):
        domain, location = get_domain_info(email)
        messagebox.showinfo("Result", f"Valid Email Address\nDomain: {domain}\nLocation: {location}")
    else:
        messagebox.showerror("Result", "Invalid Email Address")

# Create the main window
root = tk.Tk()
root.title("Email Checker")

# Create and place the widgets
tk.Label(root, text="Enter Email:").grid(row=0, column=0, padx=10, pady=10)
email_entry = tk.Entry(root, width=30)
email_entry.grid(row=0, column=1, padx=10, pady=10)

check_button = tk.Button(root, text="Check", command=check_email)
check_button.grid(row=1, column=0, columnspan=2, pady=10)

# Run the application
root.mainloop()