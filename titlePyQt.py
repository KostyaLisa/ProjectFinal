from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QCheckBox
)
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtCore import Qt
from databasePyQt import DatabaseManager
import bcrypt
import sys

class AuthApp(QWidget):
    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Система входа")
        self.setGeometry(100, 100, 400, 400)
        self.setStyleSheet("background-color: #f0f8ff;")  # Фон приложения

        layout = QVBoxLayout()

        font = QFont("Arial", 12)  # Шрифт для текста
        input_font = QFont("Arial", 14)  # Шрифт для полей ввода

        # Имя пользователя
        self.username_label = QLabel("Имя пользователя")
        self.username_label.setFont(font)
        layout.addWidget(self.username_label)

        self.username_input = QLineEdit()
        self.username_input.setFont(input_font)
        layout.addWidget(self.username_input)

        # Пароль
        self.password_label = QLabel("Пароль")
        self.password_label.setFont(font)
        layout.addWidget(self.password_label)

        self.password_input = QLineEdit()
        self.password_input.setFont(input_font)
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)

        # Показ/Скрытие пароля
        self.show_password_checkbox = QCheckBox("Показать пароль")
        self.show_password_checkbox.setFont(font)
        self.show_password_checkbox.stateChanged.connect(self.toggle_password_visibility)
        layout.addWidget(self.show_password_checkbox)

        # Кнопки Входа и Регистрации
        self.login_button = QPushButton("Вход")
        self.login_button.setFont(font)
        self.login_button.setStyleSheet("background-color: #87ceeb;")
        self.login_button.clicked.connect(self.login)
        layout.addWidget(self.login_button)

        self.register_button = QPushButton("Регистрация")
        self.register_button.setFont(font)
        self.register_button.setStyleSheet("background-color: #87ceeb;")
        self.register_button.clicked.connect(self.register)
        layout.addWidget(self.register_button)

        self.setLayout(layout)

    def toggle_password_visibility(self):
        if self.show_password_checkbox.isChecked():
            self.password_input.setEchoMode(QLineEdit.Normal)
        else:
            self.password_input.setEchoMode(QLineEdit.Password)

    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        if not username or not password:
            QMessageBox.warning(self, "Ошибка", "Заполните все поля!")
            return

        user = self.db.get_user(username)
        if user:
            stored_password, attempts, blocked = user

            if blocked:
                QMessageBox.warning(self, "Ошибка", "Этот пользователь заблокирован!")
                return

            if bcrypt.checkpw(password.encode(), stored_password):
                self.db.reset_attempts(username)
                QMessageBox.information(self, "Успех", "Вход выполнен успешно!")
                self.open_dashboard(username)
            else:
                attempts += 1
                if attempts >= 3:
                    self.db.block_user(username)
                    QMessageBox.critical(self, "Ошибка", "Ваш аккаунт заблокирован из-за 3 неудачных попыток!")
                else:
                    self.db.update_attempts(username, attempts)
                    QMessageBox.warning(self, "Ошибка", f"Неверный пароль! Попыток осталось: {3 - attempts}")
        else:
            QMessageBox.warning(self, "Ошибка", "Пользователь не найден!")

    def register(self):
        self.reg_window = RegistrationWindow(self.db)  # Сохраняем в атрибуте
        self.reg_window.show()

    def open_dashboard(self, username):
        dashboard = QWidget()
        dashboard.setWindowTitle("Личное окно")
        dashboard.setGeometry(200, 200, 400, 400)
        dashboard.setStyleSheet("background-color: #f0f8ff;")
        layout = QVBoxLayout()
        label = QLabel(f"Добро пожаловать, {username}!")
        label.setFont(QFont("Arial", 16))
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        dashboard.setLayout(layout)
        dashboard.show()

class RegistrationWindow(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Регистрация")
        self.setGeometry(150, 150, 400, 400)
        self.setStyleSheet("background-color: #f0f8ff;")
        layout = QVBoxLayout()

        font = QFont("Arial", 12)
        input_font = QFont("Arial", 14)

        # Поля для ввода
        self.username_label = QLabel("Имя пользователя")
        self.username_label.setFont(font)
        layout.addWidget(self.username_label)

        self.username_input = QLineEdit()
        self.username_input.setFont(input_font)
        layout.addWidget(self.username_input)

        self.password_label = QLabel("Пароль")
        self.password_label.setFont(font)
        layout.addWidget(self.password_label)

        self.password_input = QLineEdit()
        self.password_input.setFont(input_font)
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)

        self.confirm_label = QLabel("Повторите пароль")
        self.confirm_label.setFont(font)
        layout.addWidget(self.confirm_label)

        self.confirm_input = QLineEdit()
        self.confirm_input.setFont(input_font)
        self.confirm_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.confirm_input)

        # Кнопка "Показать пароль"
        self.show_password_checkbox = QCheckBox("Показать пароль")
        self.show_password_checkbox.setFont(font)
        self.show_password_checkbox.stateChanged.connect(self.toggle_password_visibility)
        layout.addWidget(self.show_password_checkbox)

        # Кнопка "Сохранить"
        self.save_button = QPushButton("Сохранить")
        self.save_button.setFont(font)
        self.save_button.setStyleSheet("background-color: #87ceeb;")
        self.save_button.clicked.connect(self.save_user)
        layout.addWidget(self.save_button)

        self.setLayout(layout)

    def toggle_password_visibility(self):
        if self.show_password_checkbox.isChecked():
            self.password_input.setEchoMode(QLineEdit.Normal)
            self.confirm_input.setEchoMode(QLineEdit.Normal)
        else:
            self.password_input.setEchoMode(QLineEdit.Password)
            self.confirm_input.setEchoMode(QLineEdit.Password)

    def save_user(self):
        username = self.username_input.text()
        password = self.password_input.text()
        confirm_password = self.confirm_input.text()

        if not username or not password or not confirm_password:
            QMessageBox.warning(self, "Ошибка", "Заполните все поля!")
            return

        if password != confirm_password:
            QMessageBox.warning(self, "Ошибка", "Пароли не совпадают!")
            return

        if self.db.add_user(username, password):  # Если регистрация успешна
            QMessageBox.information(self, "Успех", "Пользователь успешно зарегистрирован!")
            self.close()
        else:
            QMessageBox.warning(self, "Ошибка", "Пользователь с таким именем уже существует!")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    auth_app = AuthApp()
    auth_app.show()
    sys.exit(app.exec_())
