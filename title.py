import tkinter as tk
from tkinter import messagebox
from database import DatabaseManager
import bcrypt

class AuthApp:
    def __init__(self, root):
        self.db = DatabaseManager()
        self.root = root
        self.root.title("Login System")
        self.root.geometry("400x400")  # Set the window size
        self.root.config(bg="#f0f8ff")  # Set the background color
        self.create_main_window()

    def create_main_window(self):
        font = ("Arial", 12)  # Font for text
        entry_font = ("Arial", 14)  # Font for input fields

        tk.Label(self.root, text="Username", font=font, bg="#f0f8ff").pack(pady=5)
        self.username_entry = tk.Entry(self.root, font=entry_font)
        self.username_entry.pack(pady=5, ipady=5, ipadx=10)

        tk.Label(self.root, text="Password", font=font, bg="#f0f8ff").pack(pady=5)
        self.password_entry = tk.Entry(self.root, show="*", font=entry_font)
        self.password_entry.pack(pady=5, ipady=5, ipadx=10)

        # Button to show/hide password
        self.show_password_var = tk.BooleanVar(value=False)
        self.show_password_button = tk.Checkbutton(
            self.root, text="Show Password", variable=self.show_password_var,
            command=self.toggle_password_visibility, font=font, bg="#f0f8ff"
        )
        self.show_password_button.pack(pady=5)

        tk.Button(self.root, text="Login", command=self.login, font=font, bg="#87ceeb").pack(pady=10)
        tk.Button(self.root, text="Register", command=self.register, font=font, bg="#87ceeb").pack(pady=5)

    def toggle_password_visibility(self):
        """Toggle the visibility of the password."""
        if self.show_password_var.get():
            self.password_entry.config(show="")
        else:
            self.password_entry.config(show="*")

    def register(self):
        def save_user():
            username = username_entry.get()
            password = password_entry.get()
            confirm_password = confirm_password_entry.get()

            if not username or not password or not confirm_password:
                messagebox.showerror("Error", "All fields are required!")
                return

            if password != confirm_password:
                messagebox.showerror("Error", "Passwords do not match!")
                return

            if self.db.add_user(username, password):
                messagebox.showinfo("Success", "User registered successfully!")
                reg_window.destroy()
            else:
                messagebox.showerror("Error", "User with this name already exists!")

        font = ("Arial", 12)  # Font for text
        entry_font = ("Arial", 14)  # Font for input fields

        reg_window = tk.Toplevel()
        reg_window.title("Register")
        reg_window.geometry("400x400")
        reg_window.config(bg="#f0f8ff")

        tk.Label(reg_window, text="Username", font=font, bg="#f0f8ff").pack(pady=5)
        username_entry = tk.Entry(reg_window, font=entry_font)
        username_entry.pack(pady=5, ipady=5, ipadx=10)

        tk.Label(reg_window, text="Password", font=font, bg="#f0f8ff").pack(pady=5)
        password_entry = tk.Entry(reg_window, show="*", font=entry_font)
        password_entry.pack(pady=5, ipady=5, ipadx=10)

        tk.Label(reg_window, text="Confirm Password", font=font, bg="#f0f8ff").pack(pady=5)
        confirm_password_entry = tk.Entry(reg_window, show="*", font=entry_font)
        confirm_password_entry.pack(pady=5, ipady=5, ipadx=10)

        # Button to show/hide password
        show_password_var = tk.BooleanVar(value=False)

        def toggle_register_password_visibility():
            if show_password_var.get():
                password_entry.config(show="")
                confirm_password_entry.config(show="")
            else:
                password_entry.config(show="*")
                confirm_password_entry.config(show="*")

        show_password_button = tk.Checkbutton(
            reg_window, text="Show Password", variable=show_password_var,
            command=toggle_register_password_visibility, font=font, bg="#f0f8ff"
        )
        show_password_button.pack(pady=5)

        tk.Button(reg_window, text="Save", command=save_user, font=font, bg="#87ceeb").pack(pady=10)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showerror("Error", "All fields are required!")
            return

        user = self.db.get_user(username)
        if user:
            stored_password, attempts, blocked = user

            if blocked:
                messagebox.showerror("Error", "This user is blocked!")
                return

            if bcrypt.checkpw(password.encode(), stored_password):
                self.db.reset_attempts(username)
                messagebox.showinfo("Success", "Login successful!")
                self.user_dashboard(username)
            else:
                attempts += 1
                if attempts >= 3:
                    self.db.block_user(username)
                    messagebox.showerror("Error", "Your account has been locked after 3 failed attempts!")
                else:
                    self.db.update_attempts(username, attempts)
                    messagebox.showerror("Error", f"Incorrect password! Attempts left: {3 - attempts}")
        else:
            messagebox.showerror("Error", "User not found!")

    def user_dashboard(self, username):
        dash_window = tk.Toplevel()
        dash_window.title("Dashboard")
        dash_window.geometry("400x400")
        dash_window.config(bg="#f0f8ff")

        tk.Label(dash_window, text=f"Welcome, {username}!", font=("Arial", 16), bg="#f0f8ff").pack(pady=20)
        tk.Label(dash_window, text="Your logo will appear here.", bg="#f0f8ff").pack(pady=10)

    def run(self):
        self.root.mainloop()

    def __del__(self):
        self.db.close()
