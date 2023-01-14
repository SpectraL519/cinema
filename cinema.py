import yaml
from copy import copy

import cinema_utils as utils

# TODO:
# Salesman:
# 1. Checking customers
# 2. Checking repertoire
# 3. Issuing tickets
# Manager:
# 1. Hiring and firing staff \/
# 2. Updating / delete tickets





if __name__ == "__main__":
    print("Cinema ticket sales app\n")

    config = None

    init_user = "init"
    init_credentials = None
    init_connector = None
    connector = None
    cmd = None

    # Reading the database config file
    with open("docs/db_config.yaml", 'r') as file:
        try:
            print("Reading the config file...")
            config = yaml.safe_load(file)
            print("Success!\n")
        except yaml.YAMLError as e:
            print("Error: Reading database config")
            raise SystemExit



    # Connecting to the database as an initial user
    init_credentials = utils.Credentials(username=init_user, 
                                         password=config['credentials'][init_user])

    init_connector = utils.DBConnector(credentials=init_credentials,
                                       host=config['host'],
                                       port=config['port'],
                                       database=config['database'])

    print("Connecting to the database...")
    if not init_connector.open():
        print("Error: Database connection")
        raise SystemExit

    print("Success!")

    init_cmd = utils.CommandLine(init_connector)


    while True:
        role = init_connector.getRole(init_cmd.getCredentials())
        while not role:
            print("Error: Invalid credentials\nTry again!")
            role = init_connector.getRole(init_cmd.getCredentials())
        
        db_credentials = utils.Credentials(username=role, 
                                           password=config['credentials'][role])

        # Connect to the database with a new role
        connector = utils.DBConnector(credentials=db_credentials,
                                      host=config['host'],
                                      port=config['port'],
                                      database=config['database'])

        # Opening the application                  
        if connector.open():
            print(f"Success: Logged in as {role}")

            # Starting the application
            cmd = utils.CommandLine(connector)
            while True:
                logOut = cmd.execCommand()
                if logOut: 
                    break
            connector = None

        else:
            print("Error: Database connection\nTry again!")