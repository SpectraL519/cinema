# Imports
import os
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





class Ticket:
    def __init__(self, **kwargs):
        self.id = kwargs.get("id", None)
        self.customer = kwargs.get("customer", None)
        self.movie = kwargs.get("movie", None)
        self.start_time = kwargs.get("start_time", None)
        self.n_seats = kwargs.get("n_seats", None)
        self.seat_price = kwargs.get("seat_price", None)


    def __str__(self):
        if not all([self.id, self.movie, self.start_time, self.n_seats, self.seat_price]):
            return("Error: Invalid ticket")

        ticket = []
        ticket.append(f"Ticker nr: {self.id}")
        ticket.append('\n\t'.join([f"{key}: {self.customer[key]}" for key in self.customer.keys()]))
        ticket.append(f"Movie: {self.movie}")
        ticket.append(f"Start time: {self.start_time}")
        ticket.append(f"No. seats: {self.n_seats}")
        ticket.append(f"Price: {self.n_seats * self.seat_price}")

        return '\n\t'.join(ticket)





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

            role = self.cursor.fetchone()
            self.cursor.fetchall()
            if not role:
                return None
            return role[0]

        except mariadb.Error as e:
            print(f"Error: {e}")
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
                print(f"Error: {e}")
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
                print(f"Error: {e}")
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
                print(f"Error: {e}")
                return

            pass

        else:
            print("Error: invalid value of 'action' - must be 'show', 'hire' or 'fire'")



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
            print(f"Error: {e}")



    def displaySchedule(self, date: str):
        try:
            self.cursor.execute("""
            SELECT s.id, m.id, m.title, l.name, l.type, s.start_time, s.s_taken, r.s_max 
                FROM Schedule AS s 
                    JOIN Movies AS m ON s.movie_id = m.id
                    JOIN Languages AS l ON m.language_id = l.id
                    JOIN Rooms AS r ON s.room_id = r.id
                WHERE DATE(s.start_time) = DATE(?)
                ORDER BY m.id;
            """, (date,))

            schedule = pd.DataFrame(columns=['id', 'movie', 'start_time', 'free_seats'])
            for (s_id, m_id, title, l_name, l_type, start, s_taken, s_max) in self.cursor.fetchall():
                row = pd.DataFrame({'id': s_id,
                                    'movie': f"{m_id}: {title} ({l_name} - {l_type})",
                                    'start_time': start,
                                    'free_seats': s_max - s_taken}, index=[0])
                schedule = pd.concat([schedule, row]).reset_index(drop=True)

            print(tabulate(schedule, headers='keys', tablefmt='psql'))

        except mariadb.Error as e:
            print(f"Error: {e}")



    def getPrice(self, schedule_id: int) -> int:
        try:
            self.cursor.execute("""
            SELECT r.ticket_price
                FROM Schedule AS s JOIN Rooms AS r ON s.room_id = r.id
                WHERE s.id = ?;
            """, (schedule_id,))

            (price,) = self.cursor.fetchone()
            self.cursor.fetchall()
            if not price:
                return None
            return price

        except mariadb.Error as e:
            print(f"Error: {e}")
            return None



    def getCustomerData(self, customer_id: int) -> tuple:
        try:
            self.cursor.execute("""
            SELECT name, surname, phoneNumber, email
                FROM Customers
                WHERE id = ?
            """, (customer_id,))

            customer_data = self.cursor.fetchone()
            self.cursor.fetchone()

            if not customer_data:
                print("Error: Could not fetch customer data")
                return
            
            return customer_data

        except mariadb.Error as e:
            print(f"Error: {e}")
            return None



    def getLastTicket(self) -> int:
        try:
            self.cursor.execute("SELECT id FROM Tickets ORDER BY id DESC LIMIT 1",)

            (ticket,) = self.cursor.fetchone()
            self.cursor.fetchall()
            if not ticket:
                return None
            return ticket

        except mariadb.Error as e:
            print(f"Error: {e}")
            return None



    def manageTickets(self, action: str, **kwargs):
        if action == "showall":
            try:
                self.cursor.execute("SELECT * FROM Tickets",)
                
                tickets = pd.DataFrame(columns=['id', 'customer_id', 'schedule_id', 'n_seats'])
                for (id, customer, schedule, n_seats) in self.cursor.fetchall():
                    row = pd.DataFrame({'id': id,
                                        'customer_id': customer,
                                        'schedule_id': schedule,
                                        'n_seats': n_seats}, index=[0])
                    tickets = pd.concat([tickets, row]).reset_index(drop=True)

                print(tabulate(tickets, headers='keys', tablefmt='psql'))

            except mariadb.Error as e:
                print(f"Error: {e}")
                return

        elif action == "new":
            try:
                customer_id = kwargs.get("customer_id", 0)
                schedule_id = kwargs.get("schedule_id", None)
                n_seats = kwargs.get("n_seats", None)

                if not all([customer_id, schedule_id, n_seats]):
                    print("Error: Invalid data")
                    return

                # Add a new ticket to the database
                self.cursor.execute("""
                INSERT INTO Tickets(customer_id, schedule_id, n_seats)
                    VALUES (?, ?, ?)
                """, (customer_id, schedule_id, n_seats))

                # Extract the ticket data from the database TODO: get all customer data
                self.cursor.execute("""
                SELECT t.customer_id, s.id, m.title, l.name, l.type, s.start_time, t.n_seats
                    FROM Tickets AS t
                        JOIN Schedule AS s ON t.schedule_id = s.id
                        JOIN Movies AS m ON s.movie_id = m.id
                        JOIN Languages AS l ON m.language_id = l.id
                    WHERE t.id = (SELECT id FROM Tickets ORDER BY id DESC LIMIT 1)
                """,)

                ticket_data = self.cursor.fetchone()
                self.cursor.fetchall()

                if not ticket_data:
                    print("Error: Could not fetch ticket data")
                    return
                    
                (customer, schedule, m_title, l_name, l_type, start, seats) = ticket_data
                (c_name, c_surname, c_phone, c_email) = self.getCustomerData(customer)

                ticket = Ticket(id=self.getLastTicket(),
                                customer={'Name': c_name,
                                          'Surname': c_surname,
                                          'Phone number': c_phone,
                                          'Email': c_email},
                                movie=f"{m_title} ({l_name} - {l_type})",
                                start_time=start,
                                n_seats=seats,
                                seat_price=self.getPrice(schedule))
                print(f"\n{ticket}\n")


            except mariadb.Error as e:
                print(f"Error: {e}")
                return 

        elif action == "cancel":
            try:
                id = kwargs.get("id", None)

                if not id:
                    print("Error: Invalid data")
                    return

                self.cursor.execute("DELETE FROM Tickets WHERE id = ?", (id,))

            except mariadb.Error as e:
                print(f"Error: {e}")
                return 
            
        else:
            print("Error: invalid value of 'action' - must be 'new' or 'cancel'")


    
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
            - ticket <action> : Ticket mangement
                                <action> parameter values:
                                    - new : Adds a new ticket to the database
                                    - cancel <ticket_no> : Cancels the ticket
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
            self.connector.close()
            return True

        if args[0] == "clear":
            os.system('cls' if os.name == 'nt' else 'clear')

        elif args[0] == "help":
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

        elif args[0] == "price":
            if n_args == 1:
                print("Error: Invalid arguments")
            else:
                print(self.connector.getPrice(args[1]))

        elif args[0] == "customer":
            if n_args == 1:
                print("Error: Invalid arguments")
            else:
                print(self.connector.getCustomerData(args[1]))

        elif args[0] == "ticket":
            if n_args == 1:
                print("Error: Invalid arguments")
            else:
                if args[1] == "showall":
                    self.connector.manageTickets("showall")

                elif args[1] == "new":
                    # TODO: customer = getCustomer()
                    schedule = input("schedule_id: ")
                    seats = input("seats: ")

                    if any([(not var or var == "cancel") for var in (schedule, seats)]):
                        print()
                        return False

                    self.connector.manageTickets("new", customer_id=1,
                                                        schedule_id=schedule,
                                                        n_seats=seats)

                elif args[1] == "cancel":
                    if n_args == 2:
                        print("Error: Invalid arguments")
                    else:
                        self.connector.manageTickets("cancel", id=args[2])

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