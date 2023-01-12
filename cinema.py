import yaml
from copy import copy

import cinema_utils as utils





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
    connector = copy(init_connector)

    print("Connecting to the database...")
    if not connector.open():
        print("Error: Database connection")
        raise SystemExit

    print("Success!")



    # Starting the application
    cmd = utils.CommandLine(connector)

    while True:
        role = connector.getRole(cmd.getCredentials())
        while not role:
            print("Error: Invalid credentials\nTry again!")
            role = connector.getRole(cmd.getCredentials())
        
        db_credentials = utils.Credentials(username=role, 
                                           password=config['credentials'][role])

        # Connect to the database with a new role
        connector = utils.DBConnector(credentials=db_credentials,
                                      host=config['host'],
                                      port=config['port'],
                                      database=config['database'])
        if connector.open():
            print(f"Success: Logged in as {role}")
        else:
            connector = copy(init_connector)
            connector.open()
            continue

        while True:
            logOut = cmd.execCommand()
            if logOut: 
                connector = copy(init_connector)
                connector.open()
                break


