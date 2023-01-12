# Imports
from getpass import getpass
import re
import mariadb
import pandas as pd





class Credentials:
    def __init__(self, **kwargs):
        user = kwargs.get("username", None)
        pswd = kwargs.get("password", None)

        if checkInput(user) and checkInput(pswd):
            self.username = user
            self.password = pswd

    
    def __str__(self):
        return f"Username: {self.username}\nPassword: {self.password}"


    def __getattribute__(self, name: str):
        return object.__getattribute__(self, name)


    def isNull(self) -> bool:
        if not self.username or not self.password:
            return True

        return False

    
    def set(self, username: str, password: str) -> bool:
        if checkInput(username) and checkInput(password):
            self.username = username
            self.password = password
            return True

        print("Error: Invalid credentials\nTry again!")
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


    def new(self, **kwargs):
        # self.credentials = kwargs.get("credentials", None)
        # self.host = kwargs.get("host", None)
        # self.port = kwargs.get("port", None)
        # self.database = kwargs.get("database", None)
        return self.__class__(**kwargs)

    
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


    def getRole(self, credentials: Credentials) -> str:
        try:
            self.cursor.execute(
                "SELECT role FROM Staff WHERE username = ? AND pswd = PASSWORD(?)",
                (credentials.username, credentials.password)
            )

            R = []
            for (role,) in self.cursor.fetchall():
                R.append(role)

            if len(R) != 1:
                return None

            return R[0]

        except mariadb.Error as e:
            print(f"Error: Execute: {e}")
            return None

    
    def close(self):
        self.connection.close()
        self.connection = None





class CommandLine:
    def __init__(self, connector: DBConnector):
        self.connector = connector
        self.help = """
        Cinema application commands:
            - exit : Exits the application
        """


    def __getattribute__(self, name: str):
        return object.__getattribute__(self, name)


    def getCredentials(self) -> Credentials:
        c = Credentials()
        while True:
            username = input("\nUsername: ")
            if username == "exit":
                closeApplication(self.connector)

            password = getpass("Password: ")
            if c.set(username, password):
                break
            
        print()
        return c


    def execCommand(self, connector: DBConnector) -> bool:
        command = input("cmd> ")
        args = re.split(" ", command)

        if args[0] == "help":
            print(self.help)
            return False
            
        elif args[0] == "exit":
            return True

        else:
            print("Error: Invalid commant - To get commands' overview type 'help'")
            return False





def checkInput(input: str) -> bool:
    if not input or re.match(".*['\";, ]+.*", input):
        return False

    return True



def closeApplication(connector: DBConnector):
    if connector:
        connector.close()
    print("Bye!")
    raise SystemExit