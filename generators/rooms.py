with open("./docs/rooms.txt", 'w') as file:
    file.write("INSERT INTO Rooms(s_max) VALUES\n")
    for _ in range(4):
        file.write("\t(50),\n")
    for _ in range(4):
        file.write("\t(80),\n")
    for _ in range(2):
        file.write("\t(100),\n")
    file.write(f"\t(100);")