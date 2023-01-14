from getpass import getpass
import yaml



config = {
    'host': 'localhost',
    'port': 3306,
    'database': 'cinema',
    'credentials': {
        'init': '',
        'salesman': '',
        'manager': ''
    }
}



with open("./docs/db_config.yaml", 'w') as file:
    print("Generating config.yaml...")

    config['credentials']['init'] = getpass("Enter initial user's password: ")
    config['credentials']['salesman'] = getpass("Enter salesman's password: ")
    config['credentials']['manager'] = getpass("Enter managers's password: ")

    yaml.dump(config, file)
    print("Success!")