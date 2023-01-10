import yaml

import cinema_utils as utils





print("Cinema ticket sales app\n")

# Reading the database config file
with open("db_config.yaml", 'r') as file:
    try:
        print("Reading the db_config.yaml file...")
        config = yaml.safe_load(file)
        print("Success!\n")
    except yaml.YAMLError as e:
        print(f"Error: Reading database config: {e}")
        raise SystemExit



# Connecting to the database as an initial user
user = "init"
credentials = utils.Credentials(username=user, password=config['credentials'][user])
print(credentials)

connector = utils.DBConnector()