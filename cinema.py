import yaml
import sys
from copy import copy

import cinema_utils as utils

this = sys.modules[__name__]

# TODO:
# Salesman:
# 1. Checking customers
# 2. Checking repertoire
# 3. Issuing tickets
# Manager:
# 2. Updating / delete tickets



def _load_config():
    # Reading the database config file
    with open("docs/db_config.yaml", 'r') as file:
        try:
            print("Reading the config file...")
            this.config = yaml.safe_load(file)
            print("Success!\n")
        except yaml.YAMLError as e:
            print("Error: Reading database config")
            raise SystemExit



def _init_connection():
    print("Connecting to the database...")
    this.init_credentials = utils.Credentials(username=this.config['init_user'], 
                                              password=this.config['credentials'][this.config['init_user']])

    this.init_connector = utils.DBConnector(credentials=this.init_credentials,
                                            host=this.config['host'],
                                            port=this.config['port'],
                                            database=this.config['database'])

    if not this.init_connector.open():
        print("Error: Database connection")
        raise SystemExit
    print("Success!")



def _init():
    _load_config()
    _init_connection()



def _open_app(init_cmd: utils.Prompt):
    role = this.init_connector.get_role(init_cmd.get_credentials())
    while not role:
        print("Error: Invalid credentials\nTry again!")
        role = this.init_connector.get_role(init_cmd.get_credentials())
    
    db_credentials = utils.Credentials(username=role, 
                                        password=this.config['credentials'][role])

    # Connect to the database with a new role
    connector = utils.DBConnector(credentials=db_credentials,
                                    host=this.config['host'],
                                    port=this.config['port'],
                                    database=this.config['database'])

    # Opening the application                  
    if connector.open():
        print(f"Success: Logged in as {role}")

        # Starting the application
        cmd = utils.Prompt(connector)
        while True:
            logOut = cmd.exec()
            if logOut: 
                break
        connector = None

    else:
        print("Error: Database connection\nTry again!")



def main():
    print("Cinema ticket sales app\n")

    _init()
    init_cmd = utils.Prompt(this.init_connector)

    while True:
        _open_app(init_cmd)



if __name__ == "__main__":
    main()