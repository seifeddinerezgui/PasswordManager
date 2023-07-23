from cryptography.fernet import Fernet
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox, QFileDialog, QDialog

class PasswordManagerGUI(QtWidgets.QMainWindow):
    def __init__(self):
        super(PasswordManagerGUI, self).__init__()

        self.pm = PasswordManager()

        self.setWindowTitle("Password Manager")
        self.setMinimumSize(400, 300)

        self.centralWidget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.centralWidget)

        self.gridLayout = QtWidgets.QGridLayout(self.centralWidget)
        self.gridLayout.setContentsMargins(20, 20, 20, 20)

        self.create_key_button = QtWidgets.QPushButton("Create New Key", self)
        self.create_key_button.clicked.connect(self.create_key)
        self.gridLayout.addWidget(self.create_key_button, 0, 0)

        self.load_key_button = QtWidgets.QPushButton("Load Existing Key", self)
        self.load_key_button.clicked.connect(self.load_key)
        self.gridLayout.addWidget(self.load_key_button, 1, 0)

        self.create_password_button = QtWidgets.QPushButton("Create Password File", self)
        self.create_password_button.clicked.connect(self.create_password_file)
        self.gridLayout.addWidget(self.create_password_button, 2, 0)

        self.load_password_button = QtWidgets.QPushButton("Load Password File", self)
        self.load_password_button.clicked.connect(self.load_password_file)
        self.gridLayout.addWidget(self.load_password_button, 3, 0)

        self.add_password_button = QtWidgets.QPushButton("Add Password", self)
        self.add_password_button.clicked.connect(self.add_password)
        self.gridLayout.addWidget(self.add_password_button, 4, 0)

        self.get_password_button = QtWidgets.QPushButton("Get Password", self)
        self.get_password_button.clicked.connect(self.get_password)
        self.gridLayout.addWidget(self.get_password_button, 5, 0)

    def create_key(self):
        path, _ = QFileDialog.getSaveFileName(self, "Create New Key", "", "Key Files (*.key)")
        if path:
            self.pm.create_key(path)
            self.show_message_box("Key File Created", "Key file created successfully.")

    def load_key(self):
        path, _ = QFileDialog.getOpenFileName(self, "Load Existing Key", "", "Key Files (*.key)")
        if path:
            self.pm.load_key(path)
            self.show_message_box("Key File Loaded", "Key file loaded successfully.")

    def create_password_file(self):
        path, _ = QFileDialog.getSaveFileName(self, "Create Password File", "", "Text Files (*.txt)")
        if path:
            self.pm.create_password_file(path)
            self.show_message_box("Password File Created", "Password file created successfully.")

    def load_password_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Load Password File", "", "Text Files (*.txt)")
        if path:
            self.pm.load_password_file(path)
            self.show_message_box("Password File Loaded", "Password file loaded successfully.")

    def add_password(self):
        dialog = AddPasswordDialog(self)
        if dialog.exec_():
            site = dialog.get_site()
            password = dialog.get_password()
            if site and password:
                self.pm.add_password(site, password)
                self.show_message_box("Password Added", "Password added successfully.")

    def get_password(self):
        dialog = GetPasswordDialog(self)
        if dialog.exec_():
            site = dialog.get_site()
            password = self.pm.get_password(site)
            if password:
                self.show_message_box("Password", f"The password for {site} is: {password}")
            else:
                self.show_message_box("Password", f"No password found for {site}")

    def show_message_box(self, title, message):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.exec_()


class PasswordManager:
    def __init__(self):
        self.key = None
        self.password_file = None
        self.password_dict = {}
    def create_key(self, path):
        self.key = Fernet.generate_key()
        with open(path, 'wb') as f:
            f.write(self.key)

    def load_key(self, path):
        with open(path, 'rb') as f:
            self.key = f.read()

    def create_password_file(self, path, initial_values=None):
        self.password_file = path

        if initial_values is not None:
            for key, value in initial_values.items():
                self.add_password(key, value)

    def load_password_file(self, path):
        self.password_file = path

        with open(path, 'r') as f:
            for line in f:
                site, encrypted = line.strip().split(":")
                self.password_dict[site] = Fernet(self.key).decrypt(encrypted.encode()).decode()

    def add_password(self, site, password):
        self.password_dict[site] = password

        if self.password_file is not None:
            with open(self.password_file, 'a+') as f:
                encrypted = Fernet(self.key).encrypt(password.encode())
                f.write(site + ":" + encrypted.decode() + "\n")

    def get_password(self, site):
        return self.password_dict.get(site)


class AddPasswordDialog(QDialog):
    def __init__(self, parent=None):
        super(AddPasswordDialog, self).__init__(parent)
        self.setWindowTitle("Add Password")

        self.site_label = QtWidgets.QLabel("Site:")
        self.site_text = QtWidgets.QLineEdit()

        self.password_label = QtWidgets.QLabel("Password:")
        self.password_text = QtWidgets.QLineEdit()
        self.password_text.setEchoMode(QtWidgets.QLineEdit.Password)

        self.button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        layout = QtWidgets.QFormLayout()
        layout.addRow(self.site_label, self.site_text)
        layout.addRow(self.password_label, self.password_text)
        layout.addWidget(self.button_box)

        self.setLayout(layout)

    def get_site(self):
        return self.site_text.text()

    def get_password(self):
        return self.password_text.text()


class GetPasswordDialog(QDialog):
    def __init__(self, parent=None):
        super(GetPasswordDialog, self).__init__(parent)
        self.setWindowTitle("Get Password")

        self.site_label = QtWidgets.QLabel("Site:")
        self.site_text = QtWidgets.QLineEdit()

        self.button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        layout = QtWidgets.QFormLayout()
        layout.addRow(self.site_label, self.site_text)
        layout.addWidget(self.button_box)

        self.setLayout(layout)

    def get_site(self):
        return self.site_text.text()


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    gui = PasswordManagerGUI()
    gui.show()
    sys.exit(app.exec_())
