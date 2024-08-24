import subprocess
import sys
import os
import time
import urllib.request
import zipfile
import requests
from tkinter import Tk, Button, Label, StringVar, OptionMenu, messagebox, Frame, Toplevel
from tkinter.simpledialog import askstring
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from cryptography.fernet import Fernet

def install_packages():
    try:
        import selenium
        import cryptography
        import requests
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "selenium", "cryptography", "requests"])
        import selenium
        import cryptography
        import requests

install_packages()

current_version = "V1.0.5"
repo_base_url = "https://raw.githubusercontent.com/Boothyticklet/Roblox-account-manager/main"
version_file_url = f"{repo_base_url}/Version"
script_file_url = f"{repo_base_url}/Manager.py"

def check_for_updates():
    try:
        response = requests.get(version_file_url)
        response.raise_for_status()
        latest_version = response.text.strip()
        if latest_version.lower() != current_version.lower():
            update_script(latest_version)
        else:
            print("You are using the latest version.")
    except Exception as e:
        print(f"Failed to check for updates: {e}")

def update_script(latest_version):
    try:
        response = requests.get(script_file_url)
        response.raise_for_status()
        with open(sys.argv[0], "wb") as script_file:
            script_file.write(response.content)
        messagebox.showinfo("Update", f"The script has been updated to version {latest_version}. Please restart it.")
        sys.exit()
    except Exception as e:
        messagebox.showerror("Update Failed", f"Failed to update the script: {e}")

check_for_updates()

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
        cookie_files = ["No cookies found"]
    
    selected_cookie.set(cookie_files[0])

    menu = cookie_menu['menu']
    menu.delete(0, 'end')
    for cookie_file in cookie_files:
        menu.add_command(label=cookie_file, command=lambda value=cookie_file: selected_cookie.set(value))

def login_with_cookie(cookie_file):
    if not cookie_file or cookie_file == "No cookies found":
        return
    
    with open(os.path.join(cookie_directory, cookie_file), "r") as file:
        encrypted_cookie = file.read().strip()
        roblosecurity_cookie = decrypt(encrypted_cookie)
    
    firefox_options = Options()
    firefox_options.binary_location = firefox_binary_path
    firefox_options.add_argument("--private")
    
    service = Service(geckodriver_path)
    
    driver = webdriver.Firefox(service=service, options=firefox_options)
    driver.get("https://www.roblox.com")
    driver.add_cookie({"name": ".ROBLOSECURITY", "value": roblosecurity_cookie, "domain": "roblox.com"})
    driver.get("https://www.roblox.com/home")

def create_new_cookie_file():
    file_name = askstring("Input", "Enter a name for the account:")
    if not file_name:
        return

    file_name = f"{file_name}.txt"

    firefox_options = Options()
    firefox_options.binary_location = firefox_binary_path
    firefox_options.add_argument("--private")
    
    service = Service(geckodriver_path)
    
    driver = webdriver.Firefox(service=service, options=firefox_options)
    driver.get("https://www.roblox.com/login")
    
    while driver.current_url != "https://www.roblox.com/home":
        time.sleep(1)
    
    cookie = driver.get_cookie('.ROBLOSECURITY')
    
    if cookie:
        encrypted_cookie = encrypt(cookie['value'])
        with open(os.path.join(cookie_directory, file_name), "w") as file:
            file.write(encrypted_cookie)
        
        update_cookie_dropdown()
    
    driver.quit()

def launch_two_accounts():
    second_window = Toplevel(root)
    second_window.title("Select second account")

    second_selected_cookie = StringVar(second_window)
    cookie_files = get_cookie_files()
    if cookie_files:
        second_selected_cookie.set(cookie_files[0])
    else:
        cookie_files = ["No cookies found"]
        second_selected_cookie.set(cookie_files[0])

    second_label = Label(second_window, text="Select the second account:")
    second_label.pack(pady=5)

    second_cookie_menu = OptionMenu(second_window, second_selected_cookie, *cookie_files)
    second_cookie_menu.pack(pady=10)

    def start_accounts():
        cookie_file_1 = selected_cookie.get()
        cookie_file_2 = second_selected_cookie.get()

        if cookie_file_1 == cookie_file_2:
            messagebox.showerror("Error", "Cannot launch the same account twice.")
            return

        login_with_cookie(cookie_file_1)
        login_with_cookie(cookie_file_2)
        second_window.destroy()

    second_button = Button(second_window, text="Launch", command=start_accounts)
    second_button.pack(pady=10)

def delete_account():
    cookie_file = selected_cookie.get()
    if not cookie_file or cookie_file == "No cookies found":
        return
    
    confirm = messagebox.askyesno("Confirm", f"Are you sure you want to delete {cookie_file}?")
    if confirm:
        os.remove(os.path.join(cookie_directory, cookie_file))
        update_cookie_dropdown()

download_geckodriver()

root = Tk()
root.title("Roblox Cookie Manager")
root.geometry("300x250")

frame = Frame(root, bg="#2c3e50")
frame.place(relwidth=1, relheight=1)

label = Label(frame, text="Select an account:", bg="#2c3e50", fg="white", font=("Helvetica", 12))
label.pack(pady=5)

selected_cookie = StringVar(root)
cookie_files = get_cookie_files()
if cookie_files:
    selected_cookie.set(cookie_files[0])
else:
    cookie_files = ["No cookies found"]
    selected_cookie.set(cookie_files[0])

cookie_menu = OptionMenu(frame, selected_cookie, *cookie_files)
cookie_menu.config(bg="#34495e", fg="white", font=("Helvetica", 10))
cookie_menu["menu"].config(bg="#34495e", fg="white")
cookie_menu.pack(pady=10)

login_button = Button(frame, text="Login", command=lambda: login_with_cookie(selected_cookie.get()), bg="#3498db", fg="white", font=("Helvetica", 10))
login_button.pack(pady=5)

launch_two_button = Button(frame, text="Launch Two Accounts", command=launch_two_accounts, bg="#2ecc71", fg="white", font=("Helvetica", 10))
launch_two_button.pack(pady=5)

create_button = Button(frame, text="Create an account", command=create_new_cookie_file, bg="#95a5a6", fg="white", font=("Helvetica", 10))
create_button.pack(pady=5)

logout_button = Button(frame, text="Log out", command=delete_account, bg="#e74c3c", fg="white", font=("Helvetica", 10))
logout_button.pack(pady=5)

root.mainloop()
