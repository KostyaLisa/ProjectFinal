import tkinter as tk
from tkinter import messagebox
from database import DatabaseManager
import bcrypt

class AuthApp:
    def __init__(self, root):
        self.db = DatabaseManager()
        self.root = root
        self.root.title("Система входа")
        self.root.geometry("400x400")  # Устанавливаем размер окна
        self.root.config(bg="#f0f8ff")  # Устанавливаем цвет фона
        self.create_main_window()

    def create_main_window(self):
        font = ("Arial", 12)  # Шрифт для текста
        entry_font = ("Arial", 14)  # Шрифт для полей ввода

        tk.Label(self.root, text="Имя пользователя", font=font, bg="#f0f8ff").pack(pady=5)
        self.username_entry = tk.Entry(self.root, font=entry_font)
        self.username_entry.pack(pady=5, ipady=5, ipadx=10)

        tk.Label(self.root, text="Пароль", font=font, bg="#f0f8ff").pack(pady=5)
        self.password_entry = tk.Entry(self.root, show="*", font=entry_font)
        self.password_entry.pack(pady=5, ipady=5, ipadx=10)

        # Кнопка для показа/скрытия пароля
        self.show_password_var = tk.BooleanVar(value=False)
        self.show_password_button = tk.Checkbutton(
            self.root, text="Показать пароль", variable=self.show_password_var,
            command=self.toggle_password_visibility, font=font, bg="#f0f8ff"
        )
        self.show_password_button.pack(pady=5)

        tk.Button(self.root, text="Вход", command=self.login, font=font, bg="#87ceeb").pack(pady=10)
        tk.Button(self.root, text="Регистрация", command=self.register, font=font, bg="#87ceeb").pack(pady=5)

    def toggle_password_visibility(self):
        """Переключение показа/скрытия пароля."""
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
                messagebox.showerror("Ошибка", "Заполните все поля!")
                return

            if password != confirm_password:
                messagebox.showerror("Ошибка", "Пароли не совпадают!")
                return

            if self.db.add_user(username, password):
                messagebox.showinfo("Успех", "Пользователь успешно зарегистрирован!")
                reg_window.destroy()
            else:
                messagebox.showerror("Ошибка", "Пользователь с таким именем уже существует!")

        font = ("Arial", 12)  # Шрифт для текста
        entry_font = ("Arial", 14)  # Шрифт для полей ввода

        reg_window = tk.Toplevel()
        reg_window.title("Регистрация")
        reg_window.geometry("400x400")
        reg_window.config(bg="#f0f8ff")

        tk.Label(reg_window, text="Имя пользователя", font=font, bg="#f0f8ff").pack(pady=5)
        username_entry = tk.Entry(reg_window, font=entry_font)
        username_entry.pack(pady=5, ipady=5, ipadx=10)

        tk.Label(reg_window, text="Пароль", font=font, bg="#f0f8ff").pack(pady=5)
        password_entry = tk.Entry(reg_window, show="*", font=entry_font)
        password_entry.pack(pady=5, ipady=5, ipadx=10)

        tk.Label(reg_window, text="Повторите пароль", font=font, bg="#f0f8ff").pack(pady=5)
        confirm_password_entry = tk.Entry(reg_window, show="*", font=entry_font)
        confirm_password_entry.pack(pady=5, ipady=5, ipadx=10)

        # Кнопка для показа/скрытия пароля
        show_password_var = tk.BooleanVar(value=False)

        def toggle_register_password_visibility():
            if show_password_var.get():
                password_entry.config(show="")
                confirm_password_entry.config(show="")
            else:
                password_entry.config(show="*")
                confirm_password_entry.config(show="*")

        show_password_button = tk.Checkbutton(
            reg_window, text="Показать пароль", variable=show_password_var,
            command=toggle_register_password_visibility, font=font, bg="#f0f8ff"
        )
        show_password_button.pack(pady=5)

        tk.Button(reg_window, text="Сохранить", command=save_user, font=font, bg="#87ceeb").pack(pady=10)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showerror("Ошибка", "Заполните все поля!")
            return

        user = self.db.get_user(username)
        if user:
            stored_password, attempts, blocked = user

            if blocked:
                messagebox.showerror("Ошибка", "Этот пользователь заблокирован!")
                return

            if bcrypt.checkpw(password.encode(), stored_password):
                self.db.reset_attempts(username)
                messagebox.showinfo("Успех", "Вход выполнен успешно!")
                self.user_dashboard(username)
            else:
                attempts += 1
                if attempts >= 3:
                    self.db.block_user(username)
                    messagebox.showerror("Ошибка", "Ваш аккаунт заблокирован из-за 3 неудачных попыток!")
                else:
                    self.db.update_attempts(username, attempts)
                    messagebox.showerror("Ошибка", f"Неверный пароль! Попыток осталось: {3 - attempts}")
        else:
            messagebox.showerror("Ошибка", "Пользователь не найден!")

    def user_dashboard(self, username):
        dash_window = tk.Toplevel()
        dash_window.title("Личное окно")
        dash_window.geometry("400x400")
        dash_window.config(bg="#f0f8ff")

        tk.Label(dash_window, text=f"Добро пожаловать, {username}!", font=("Arial", 16), bg="#f0f8ff").pack(pady=20)
        tk.Label(dash_window, text="Ваш логотип будет здесь.", bg="#f0f8ff").pack(pady=10)

    def run(self):
        self.root.mainloop()

    def __del__(self):
        self.db.close()
