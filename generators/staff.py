def generate(role: str, no: int):
    username = f"{role}_{no}"
    password = f"{role}_password_{no}"
    return f"INSERT INTO Staff(username, pswd, role) VALUES('{username}', PASSWORD('{password}'), '{role}');\n"


with open("./docs/staff.txt", 'w') as file:
    file.write(generate("manager", 1))

    for no in range(1, 5):
        file.write(generate("salesman", no))