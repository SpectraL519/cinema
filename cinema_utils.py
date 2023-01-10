# Imports
from getpass import getpass
import re
import mariadb
import pandas as pd





class Credentials:
    def __init__(self, **kwargs):
        self.username = kwargs.get("username", None)
        self.password = kwargs.get("password", None) if self.username else None

    
    def __str__(self):
        return f"Username: {self.username}\nPassword: {self.password}"


    def __getattribute__(self, name: str):
        return object.__getattribute__(self, name)


    def isNull(self) -> bool:
        if not self.username or not self.password:
            return True

        return False


    def checkInput(self, input: str) -> bool:
        if not input or re.match(".*['\";, ]+.*", input):
            return False

        return True

    
    def set(self, username: str, password: str) -> bool:
        if self.checkInput(username) and self.checkInput(password):
            self.username = username
            self.password = password
            return True

        print("Error: Invalid credentials")
        return False





class DBConnector:
    def __init__(self, **kwargs):
        self.credentials = kwargs.get("credentials", None)
        self.host = kwargs.get("host", None)
        self.port = kwargs.get("port", None)
        self.database = kwargs.get("database", None)
        self.connection = None
        self.cursor = None

    
    def __getattribute__(self, name: str):
        return object.__getattribute__(self, name)


    def setParams(self, **kwargs):
        self.credentials = kwargs.get("credentials", None)
        self.host = kwargs.get("host", None)
        self.port = kwargs.get("port", None)
        self.database = kwargs.get("database", None)

    
    def open(self) -> bool:
        try:
            self.connection = mariadb.connect(
                user=self.credentials.username,
                password=self.credentials.password,
                host=self.host,
                port=self.port,
                database=self.database
            )
            self.cursor = self.connection.cursor()
            return True

        except mariadb.Error as e:
            print(f"Error: MariaDB connection: {e}")
            return False


    def testSelect(self):
        try:
            self.cursor.execute(
                "SELECT * FROM Staff"
            )
        except mariadb.Error as e:
            print(f"Error: Execute: {e}")
            return None

        U, P, R = [], [], []
        for (user, pswd, role) in self.cursor:
            U.append(user)
            P.append(pswd)
            R.append(role)
        
        return pd.DataFrame({'user': U,
                             'password': P,
                             'role': R})

    
    def close(self):
        self.connection.close()





class CommandLine:
    def __init__(self, **kwargs):
        self.credentials = kwargs.get("credentials", None)
        self.connector = kwargs.get("connector", None)


    def __getattribute__(self, name: str):
        return object.__getattribute__(self, name)


    def EXIT_MESSAGE(self) -> str:
        return "Bye!"


    def getCredentials(self) -> Credentials:
        c = Credentials()
        while True:
            username = input("Username: ")
            password = getpass("Password: ")
            c.set(username, password)
            if not c.isNull():
                break
            
        return c


    def execCommand(self, connector: DBConnector):
        command = input("cmd> ")
        args = re.split(" ", command)

        if args[0] == "help":
            pass
            
        elif args[0] == "exit":
            raise SystemExit