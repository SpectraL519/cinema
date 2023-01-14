# Imports
from getpass import getpass
import re
import mariadb
import pandas as pd
from datetime import datetime
from tabulate import tabulate





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
        self.engine = None
        self.connection = None
        self.cursor = None

    
    def __getattribute__(self, name: str):
        return object.__getattribute__(self, name)

    
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
            print(f"Error: EXECUTE: {e}")
            return None


    def manageStaff(self, action: str, **kwargs):
        if action == "show":
            try:
                self.cursor.execute("SELECT username, role FROM Staff",)

                staff = pd.DataFrame(columns=['username', 'role'])
                for (user, role) in self.cursor.fetchall():
                    row = pd.DataFrame({'username': user,
                                        'role': role}, index=[0])
                    staff = pd.concat([staff, row]).reset_index(drop=True)

                print(tabulate(staff, headers='keys', tablefmt='psql'))

            except mariadb.Error as e:
                print(f"Error: EXECUTE: {e}")
                return

        elif action == "hire":
            try:
                credentials = kwargs.get("credentials", None)
                if not credentials:
                    print("Error: Invalid credentials")
                    return

                self.cursor.execute("""
                INSERT INTO Staff(username, pswd, role)
                    VALUES(?, PASSWORD(?), 'salesman')
                """, (credentials.username, credentials.password))
                
                self.manageStaff("show")

            except mariadb.Error as e:
                print(f"Error: EXECUTE: {e}")
                return 

        elif action == "fire":
            try:
                user = kwargs.get("username", None)
                if not user:
                    print("Error: Invalid user")
                    return

                self.cursor.execute("DELETE FROM Staff WHERE username = ?", (user,))
                
                self.manageStaff("show")

            except mariadb.Error as e:
                print(f"Error: EXECUTE: {e}")
                return

            pass

        else:
            print("Error: invalid value of 'action' - must be 'show', 'hire' or 'fire'")
            return        


    def displayRepertoire(self, date: str):
        try:
            self.cursor.execute("""
            SELECT DISTINCT(m.title)
                FROM Schedule AS s JOIN Movies AS m ON s.movie_id = m.id
                WHERE DATE(s.start_time) = DATE(?)
                ORDER BY m.title;
            """, (date,))

            schedule = pd.DataFrame(columns=['title'])
            for (title) in self.cursor.fetchall():
                row = pd.DataFrame({'title': title}, index=[0])
                schedule = pd.concat([schedule, row]).reset_index(drop=True)

            print(tabulate(schedule, headers='keys', tablefmt='psql'))

        except mariadb.Error as e:
            print(f"Error: EXECUTE: {e}")
            return None


    def displaySchedule(self, date: str):
        try:
            self.cursor.execute("""
            SELECT m.id, m.title, l.name, l.type, s.start_time, s.s_taken, r.s_max 
                FROM Schedule AS s 
                    JOIN Movies AS m ON s.movie_id = m.id
                    JOIN Languages AS l ON m.language_id = l.id
                    JOIN Rooms AS r ON s.room_id = r.id
                WHERE DATE(s.start_time) = DATE(?)
                ORDER BY m.title;
            """, (date,))

            schedule = pd.DataFrame(columns=['id', 'title', 'language', 'start_time', 'free_seats'])
            for (id, title, l_name, l_type, start, s_taken, s_max) in self.cursor.fetchall():
                row = pd.DataFrame({'id': id,
                                    'title': title,
                                    'language': f"{l_name} ({l_type})",
                                    'start_time': start,
                                    'free_seats': s_max - s_taken}, index=[0])
                schedule = pd.concat([schedule, row]).reset_index(drop=True)

            print(tabulate(schedule, headers='keys', tablefmt='psql'))

        except mariadb.Error as e:
            print(f"Error: EXECUTE: {e}")
            return None

    
    def close(self):
        self.connection.commit()
        self.connection.close()
        self.connection = None





class CommandLine:
    def __init__(self, connector: DBConnector):
        self.connector = connector
        self.help = """
        Cinema application commands:
            - repertoire <date> : Displays all movies played on the <date>
                                  If the <date> parameters is not specified it will be set to the current system date
            - schedule <date> : Displays all movies with their language, start time and free seats count on the <date>
                                If the <date> parameters is not specified it will be set to the current system date
            - staff <action> : Staff management:
                               <action> parameter values:
                                    - show : Displays all staff members
                                    - hire : Adds a new salesman to the staff
                                    - fire <username> : Removes a salesman from staff
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

            if username == "cancel":
                return None

            password = getpass("Password: ")
            if c.set(username, password):
                break
            
        print()
        return c


    def execCommand(self) -> bool:
        command = input("cmd> ")
        args = re.split(" ", command)
        n_args = len(args)

        if n_args == 0:
            return False
            
        if args[0] == "exit":
            closeApplication(self.connector)

        if args[0] == "logOut":
            return True

        if args[0] == "help":
            print(self.help)

        elif args[0] == "staff":
            if n_args < 2:
                print("Error: Invalid arguments")
                return

            if args[1] == "show":
                self.connector.manageStaff("show")

            elif args[1] == "hire":
                hire = self.getCredentials()
                if hire:
                    self.connector.manageStaff("hire", credentials=hire)

            elif args[1] == "fire":
                user = input("Username: ")
                if not user or user == "cancel":
                    return False

                self.connector.manageStaff("fire", username=user)

        elif args[0] == "repertoire":
            if n_args == 1:
                self.connector.displayRepertoire(datetime.today().strftime('%Y-%m-%d'))
            else:
                self.connector.displayRepertoire(args[1])

        elif args[0] == "schedule":
            if n_args == 1:
                self.connector.displaySchedule(datetime.today().strftime('%Y-%m-%d'))
            else:
                self.connector.displaySchedule(args[1])

        elif args[0] == "ticket":
            if n_args == 1:
                print("Error: Invalid arguments")
            else:
                if args[1] == "new":
                    pass
                else:
                    print("Error: Invalid arguments")


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