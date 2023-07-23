from cryptography.fernet import Fernet


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


def main():
    password = {
        "email": "123456",
        "facebook": "myfbpwd",
        "github": "mygitpwd",
        "crax.pro": "akwaspammer"
    }

    pm = PasswordManager()

    print("""************** WHAT DO YOU WANT TO DO **************
          (1) Create a new key
          (2) Load an existing Key
          (3) Create a new password file
          (4) Load an existing password file
          (5) Add a new password
          (6) Get a password
          (q) Quit""")
    done = False
    while not done:
        choice = input("Enter your choice: ")
        if choice == "1":
            path = input("Enter the path to save the key file: ")
            pm.create_key(path)
            print("Key file created.")
        elif choice == "2":
            path = input("Enter the path to load the key file: ")
            pm.load_key(path)
            print("Key file loaded.")
        elif choice == "3":
            path = input("Enter the path to create the password file: ")
            pm.create_password_file(path, password)
            print("Password file created.")
        elif choice == "4":
            path = input("Enter the path to load the password file: ")
            pm.load_password_file(path)
            print("Password file loaded.")
        elif choice == "5":
            site = input("Enter the site: ")
            password = input("Enter the password: ")
            pm.add_password(site, password)
            print("Password added.")
        elif choice == "6":
            site = input("Enter the site to retrieve the password: ")
            password = pm.get_password(site)
            if password is not None:
                print(f"Password for {site}: {password}")
            else:
                print(f"No password found for {site}")
        elif choice == "q":
            done = True
            print("Goodbye!")
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
