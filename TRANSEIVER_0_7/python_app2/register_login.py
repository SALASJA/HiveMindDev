#import modules

from tkinter import *
from PIL import Image, ImageTk
from cryptography.fernet import Fernet
import os
import base64
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# handles register window
def register():

    global register_window
    global user
    global pw
    global user_entry
    global pw_entry


    register_window = Toplevel(main_window)
    register_window.title("Register")
    register_window.geometry("400x350")
    register_window.resizable(width=False, height=False)

# Set username/password variables
    user = StringVar()
    pw = StringVar()

# Set label for user's instruction
    Label(register_window, text="Please fill out the following", bg="gray").pack()
    Label(register_window, text="").pack()

# Set username label
    user_label = Label(register_window, text="Username * ")
    user_label.pack()

# Set username entry
    user_entry = Entry(register_window, textvariable = user)
    user_entry.pack()

# Set password label
    pw_label = Label(register_window, text="Password * ")
    pw_label.pack()

# Set password entry
    pw_entry = Entry(register_window, textvariable = pw, show='*')
    pw_entry.pack()

    Label(register_window, text="").pack()

# Set register button
    Button(register_window, text="Register", width=10, height=1, bg="gray", command = user_register).pack()

# handles user registration
def user_register():

# getters for username and password
    user_info = user.get()
    pw_info = pw.get()

# Open file in write mode
    if not os.path.exists(user_info + '.txt'):
        file = open(user_info + '.txt', "wb")

# write username and password information into file
        password_provided = pw_info

    
        key = b'TGgdgV197X9imuoNn3xy697Ap1-zzCsRuTI6E8WV8IU=' 
        f = Fernet(key)
    
        encoded_text = f.encrypt(bytes(pw_info, encoding= 'utf-8'))

        file.write(encoded_text)
        file.close()

        user_entry.delete(0, END)
        pw_entry.delete(0, END)

        Label(register_window, text = "You have successfully registered!", fg = "green", font = ("Calibri", 11)).pack()

        register_window.after(2000, lambda: register_window.destroy())
    else:
        user_already_exists()

# define login function
def login():
    global login_window
    login_window = Toplevel(main_window)
    login_window.title("Login")
    login_window.geometry("400x350")
    login_window.resizable(width=False, height=False)
    Label(login_window, text = "Please fill out to login").pack()
    Label(login_window, text = "").pack()

    global user_verify
    global pw_verify

    user_verify = StringVar()
    pw_verify = StringVar()

    global user_login_entry
    global pw_login_entry

    Label(login_window, text="Username * ").pack()
    user_login_entry = Entry(login_window, textvariable = user_verify)
    user_login_entry.pack()
    Label(login_window, text = "").pack()
    Label(login_window, text = "Password * ").pack()
    pw_login_entry = Entry(login_window, textvariable= pw_verify, show = '*')
    pw_login_entry.pack()
    Label(login_window, text = "").pack()
    Button(login_window, text = "Login", width = 10, height = 1, command = login_verify).pack()

def login_verify():

# get username and password
    password = pw_verify.get()
    
    key = b'TGgdgV197X9imuoNn3xy697Ap1-zzCsRuTI6E8WV8IU='
    f = Fernet(key)
    username = user_verify.get()

# this will delete the entry after login button is pressed
    user_login_entry.delete(0, END)
    pw_login_entry.delete(0, END)

# The method listdir() returns a list containing the names of the entries in the directory given by path.
    list_of_files = os.listdir()

#defining verification's conditions
    if username + '.txt' in list_of_files:
        file1 = open(username + '.txt', "rb") # open the file in read mode
        verify = file1.read()

        encrypted = f.decrypt(verify)
        original = encrypted.decode()
        print(original)
        
        if password == original:
            login_success()
        else:
            pw_not_recognized()

    else:
        user_not_found()

def user_already_exists():
    global user_already_exists_window
    user_already_exists_window = Toplevel(register_window)
    user_already_exists_window.title("Error")
    user_already_exists_window.geometry("150x100")
    Label(user_already_exists_window, text="User already exists!").pack()
    Button(user_already_exists_window, text="OK", command=delete_user_already_exists).pack()

# Designing popup for login success

def login_success():
    global login_success_window
    login_success_window = Toplevel(login_window)
    login_success_window.title("Success")
    login_success_window.geometry("150x100")
    Label(login_success_window, text="Login Success").pack()
    Button(login_success_window, text="OK", command=delete_login_success).pack()

# Designing popup for login invalid password

def pw_not_recognized():
    global pw_not_recognized_window
    pw_not_recognized_window = Toplevel(login_window)
    pw_not_recognized_window.title("Error")
    pw_not_recognized_window.geometry("150x100")
    Label(pw_not_recognized_window, text="Invalid Password ").pack()
    Button(pw_not_recognized_window, text="OK", command=delete_pw_not_recognized).pack()

# Designing popup for user not found
 
def user_not_found():
    global user_not_found_window
    user_not_found_window = Toplevel(login_window)
    user_not_found_window.title("Error")
    user_not_found_window.geometry("150x100")
    Label(user_not_found_window, text="User Not Found").pack()
    Button(user_not_found_window, text="OK", command=delete_user_not_found_window).pack()

# Deleting popups
def delete_user_already_exists():
    user_already_exists_window.destroy()

def delete_login_success():
    login_success_window.destroy()
    main_window.destroy()


def delete_pw_not_recognized():
    pw_not_recognized_window.destroy()


def delete_user_not_found_window():
    user_not_found_window.destroy()


def main_account_window():
    global main_window

    main_window = Tk()   # create a GUI window
    main_window.geometry("250x520") # set the size of GUI window
    main_window.resizable(width=False, height=False)
    main_window.title("HiveMind") # set the title of GUI window

    # Form label
    Label(text="Please Login Or Register", bg="gray", width="100", height="2", font=("Courier New", 13)).pack()
    Label(text="").pack()

    # Login Button
    Button(text="Login", height="2", width="30", command = login).pack()
    Label(text="").pack()

    # Register button
    Button(text="Register", height="2", width="30", command = register).pack()
    Label(text="").pack()

    Label(text="", bg="gray", width="100", height="19", font=("Courier New", 13)).pack()
    load = Image.open("logo.png")
    render = ImageTk.PhotoImage(load)

    img = Label(main_window, image=render)
    img.image = render
    img.place(x=0, y=190)

    main_window.mainloop() # start the GUI

main_account_window() # call the main_account_screen() function
