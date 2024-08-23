import os
import time
import urllib.request
import zipfile
import requests
from tkinter import Tk, Button, Label, StringVar, OptionMenu, messagebox, Frame
from tkinter.simpledialog import askstring
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from cryptography.fernet import Fernet


CURRENT_VERSION = "V1.0.0"
repo_base_url = "https://raw.githubusercontent.com/Boothyticklet/Roblox-account-manager/main"
version_file_url = f"{repo_base_url}/Version"
script_file_url = f"{repo_base_url}/Manager.py"

def check_for_updates():
    try:
        response = requests.get(version_file_url)
        response.raise_for_status()
        latest_version = response.text.strip()
        if CURRENT_VERSION != latest_version:
            if messagebox.askyesno("Update Available", f"A new version {latest_version} is available. Do you want to update?"):
                update_script()
    except Exception as e:
        print(f"Failed to check for updates: {e}")

def update_script():
    try:
        response = requests.get(script_file_url)
        response.raise_for_status()
        with open(__file__, "wb") as script_file:
            script_file.write(response.content)
        messagebox.showinfo("Update Complete", "The application has been updated to the latest version.")
        os.execv(__file__, [])
    except Exception as e:
        print(f"Failed to update script: {e}")


geckodriver_url = "https://github.com/mozilla/geckodriver/releases/download/v0.35.0/geckodriver-v0.35.0-win32.zip"
geckodriver_zip = "geckodriver.zip"
requirements_folder = os.path.join(os.getcwd(), "Requirements")
geckodriver_path = os.path.join(requirements_folder, "geckodriver.exe")
firefox_binary_path = r'C:\Program Files\Mozilla Firefox\firefox.exe'
cookie_directory = os.getcwd()
key_file = os.path.join(requirements_folder, "secret.key")


def load_key():
    if not os.path.exists(requirements_folder):
        os.makedirs(requirements_folder)
    if os.path.exists(key_file):
        return open(key_file, "rb").read()
    else:
        key = Fernet.generate_key()
        with open(key_file, "wb") as key_file_out:
            key_file_out.write(key)
        return key

encryption_key = load_key()
cipher = Fernet(encryption_key)

def encrypt(data):
    return cipher.encrypt(data.encode()).decode()

def decrypt(data):
    return cipher.decrypt(data.encode()).decode()


def download_geckodriver():
    if not os.path.exists(requirements_folder):
        os.makedirs(requirements_folder)
    
    if not os.path.exists(geckodriver_path):
        urllib.request.urlretrieve(geckodriver_url, os.path.join(requirements_folder, geckodriver_zip))
        with zipfile.ZipFile(os.path.join(requirements_folder, geckodriver_zip), 'r') as zip_ref:
            zip_ref.extractall(requirements_folder)
        os.remove(os.path.join(requirements_folder, geckodriver_zip))


def get_cookie_files():
    return [f for f in os.listdir(cookie_directory) if f.endswith(".txt")]


def update_cookie_dropdown():
    cookie_files = get_cookie_files()
    if not cookie_files:
        cookie_files = ["No Accounts found"]
    selected_cookie.set(cookie_files[0])

    menu = cookie_menu['menu']
    menu.delete(0, 'end')
    for cookie_file in cookie_files:
        menu.add_command(label=cookie_file, command=lambda value=cookie_file: selected_cookie.set(value))


def login_with_cookie():
    cookie_file = selected_cookie.get()
    if not cookie_file or cookie_file == "No cookies found":
        return
    
    with open(os.path.join(cookie_directory, cookie_file), "r") as file:
        encrypted_cookie = file.read().strip()
        roblosecurity_cookie = decrypt(encrypted_cookie)
    
    driver = create_driver()
    driver.get("https://www.roblox.com")
    driver.add_cookie({"name": ".ROBLOSECURITY", "value": roblosecurity_cookie, "domain": "roblox.com"})
    driver.get("https://www.roblox.com/home")


def create_new_cookie_file():
    file_name = askstring("Input", "Enter a name for the account:")
    if not file_name:
        return

    file_name = f"{file_name}.txt"

    driver = create_driver()
    driver.get("https://www.roblox.com/login")
    
    while "home" not in driver.current_url:
        time.sleep(1)
    
    cookie = driver.get_cookie('.ROBLOSECURITY')
    
    if cookie:
        encrypted_cookie = encrypt(cookie['value'])
        with open(os.path.join(cookie_directory, file_name), "w") as file:
            file.write(encrypted_cookie)
        
        update_cookie_dropdown()
    
    driver.quit()


def remove_cookie_file():
    cookie_file = selected_cookie.get()
    if not cookie_file or cookie_file == "No cookies found":
        return
    
    if messagebox.askyesno("Confirmation", f"Are you sure you want to delete {cookie_file}?"):
        os.remove(os.path.join(cookie_directory, cookie_file))
        update_cookie_dropdown()


def create_driver():
    firefox_options = Options()
    firefox_options.binary_location = firefox_binary_path
    firefox_options.add_argument("--private")
    
    service = Service(geckodriver_path)
    return webdriver.Firefox(service=service, options=firefox_options)


def launch_two_accounts():
    first_cookie = selected_cookie.get()
    if not first_cookie or first_cookie == "No cookies found":
        messagebox.showwarning("Warning", "No valid Account selected.")
        return
    
    update_cookie_dropdown()
    second_cookie = selected_cookie.get()

    if first_cookie == second_cookie or not second_cookie or second_cookie == "No cookies found":
        messagebox.showwarning("Warning", "Select a different Account.")
        return

    
    with open(os.path.join(cookie_directory, first_cookie), "r") as file:
        encrypted_cookie = file.read().strip()
        roblosecurity_cookie = decrypt(encrypted_cookie)
    
    driver1 = create_driver()
    driver1.get("https://www.roblox.com")
    driver1.add_cookie({"name": ".ROBLOSECURITY", "value": roblosecurity_cookie, "domain": "roblox.com"})
    driver1.get("https://www.roblox.com/home")

    
    with open(os.path.join(cookie_directory, second_cookie), "r") as file:
        encrypted_cookie = file.read().strip()
        roblosecurity_cookie = decrypt(encrypted_cookie)
    
    driver2 = create_driver()
    driver2.get("https://www.roblox.com")
    driver2.add_cookie({"name": ".ROBLOSECURITY", "value": roblosecurity_cookie, "domain": "roblox.com"})
    driver2.get("https://www.roblox.com/home")

download_geckodriver()


check_for_updates()


root = Tk()
root.title("Roblox Account Manager")
root.geometry("500x450")
root.configure(bg='#1a1a1a')


title_frame = Frame(root, bg='#343a40')
title_frame.pack(fill='x')

label_title = Label(title_frame, text="Roblox Account Manager", font=('Arial', 18), bg='#343a40', fg='white')
label_title.pack(pady=10)


account_frame = Frame(root, bg='#1a1a1a')
account_frame.pack(pady=10)

label_select = Label(account_frame, text="Select an account:", bg='#1a1a1a', fg='white')
label_select.grid(row=0, column=0, pady=5)

selected_cookie = StringVar(root)
cookie_files = get_cookie_files()
selected_cookie.set(cookie_files[0] if cookie_files else "No Accounts found")

cookie_menu = OptionMenu(account_frame, selected_cookie, *cookie_files)
cookie_menu.config(bg='#343a40', fg='white', activebackground='#495057', width=20)
cookie_menu.grid(row=0, column=1, pady=5)


button_frame = Frame(root, bg='#1a1a1a')
button_frame.pack(pady=10)

login_button = Button(button_frame, text="Login", command=login_with_cookie, bg='#007bff', fg='white', activebackground='#0056b3', width=18)
login_button.grid(row=0, column=0, padx=5, pady=5)

create_button = Button(button_frame, text="Create an account", command=create_new_cookie_file, bg='#6c757d', fg='white', activebackground='#5a6268', width=18)
create_button.grid(row=0, column=1, padx=5, pady=5)

remove_button = Button(button_frame, text="Log out", command=remove_cookie_file, bg='#dc3545', fg='white', activebackground='#c82333', width=18)
remove_button.grid(row=1, column=0, padx=5, pady=5)

launch_two_button = Button(button_frame, text="Launch Two Accounts", command=launch_two_accounts, bg='#28a745', fg='white', activebackground='#218838', width=18)
launch_two_button.grid(row=1, column=1, padx=5, pady=5)

root.mainloop()
