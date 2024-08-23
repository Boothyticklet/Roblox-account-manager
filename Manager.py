import subprocess
import sys
import os
import time
import urllib.request
import zipfile
from tkinter import Tk, Button, Label, StringVar, OptionMenu, messagebox, Frame
from tkinter.simpledialog import askstring
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from cryptography.fernet import Fernet


def install_packages():
    try:
        import selenium
        import cryptography
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "selenium", "cryptography"])
        import selenium
        import cryptography

install_packages()

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


def login_with_cookie():
    cookie_file = selected_cookie.get()
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

    messagebox.showinfo("Info", "The browser will remain open. Press OK to close.")
    driver.quit()


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

    while "home" not in driver.current_url:
        time.sleep(1)

    cookie = driver.get_cookie('.ROBLOSECURITY')

    if cookie:
        encrypted_cookie = encrypt(cookie['value'])
        with open(os.path.join(cookie_directory, file_name), "w") as file:
            file.write(encrypted_cookie)

        update_cookie_dropdown()

    driver.quit()


def join_vip():
    cookie_file = selected_cookie.get()
    if not cookie_file or cookie_file == "No cookies found":
        return

    url = askstring("VIP Server", "Enter the VIP server URL:")
    if not url:
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
    driver.get(url)

    messagebox.showinfo("Info", "The browser will remain open. Press OK to close.")
    driver.quit()


def delete_cookie_file():
    cookie_file = selected_cookie.get()
    if not cookie_file or cookie_file == "No cookies found":
        return

    confirm = messagebox.askyesno("Delete", f"Are you sure you want to delete {cookie_file}?")
    if confirm:
        os.remove(os.path.join(cookie_directory, cookie_file))
        update_cookie_dropdown()


download_geckodriver()

root = Tk()
root.title("Roblox Cookie Manager")
root.configure(bg="#2C3E50")

frame = Frame(root, bg="#34495E", padx=10, pady=10)
frame.pack(padx=10, pady=10)

title_label = Label(frame, text="Roblox Cookie Manager", font=("Arial", 16, "bold"), bg="#34495E", fg="white")
title_label.grid(row=0, column=0, columnspan=3, pady=10)

label = Label(frame, text="Select an account:", font=("Arial", 12), bg="#34495E", fg="white")
label.grid(row=1, column=0, pady=5)

selected_cookie = StringVar(root)
cookie_files = get_cookie_files()
if cookie_files:
    selected_cookie.set(cookie_files[0])
else:
    cookie_files = ["No cookies found"]
    selected_cookie.set(cookie_files[0])

cookie_menu = OptionMenu(frame, selected_cookie, *cookie_files)
cookie_menu.grid(row=1, column=1, pady=5)

login_button = Button(frame, text="Login", font=("Arial", 12), bg="#2980B9", fg="white", command=login_with_cookie)
login_button.grid(row=2, column=0, padx=5, pady=10)

create_button = Button(frame, text="Create an account", font=("Arial", 12), bg="#27AE60", fg="white", command=create_new_cookie_file)
create_button.grid(row=2, column=1, padx=5, pady=10)

delete_button = Button(frame, text="Log out", font=("Arial", 12), bg="#E74C3C", fg="white", command=delete_cookie_file)
delete_button.grid(row=2, column=2, padx=5, pady=10)

vip_button = Button(frame, text="Join VIP", font=("Arial", 14), bg="#2ECC71", fg="white", command=join_vip)
vip_button.grid(row=3, column=0, columnspan=3, pady=10)

root.mainloop()
