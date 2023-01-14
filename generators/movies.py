movies = [("Whitney Houston: I Wanna Dance With Somebody", 146),
          ("Shotgun Wedding", 101),
          ("Puss in Boots: The Last Wish", 100),
          ("Transformers: Rise of the Beasts", 150),
          ("Mission: Impossible - Dead Reckoning Part One", 150),
          ("Spider-Man: Across the Sipder-Verse", 115),
          ("The Marvels", 135),
          ("Fast & Furious 10", 145),
          ("Ant-Man and the Wasp: Quantumania", 125),
          ("John Wick: Chapter 4", 130),
          ("Avatar: The Way of Water", 193)]


with open("./docs/movies.txt", 'w') as file:
    file.write("INSERT INTO Movies(title, length, language_id) VALUES\n")
    for movie in movies[:-1]:
        for lang in range(1, 5):
            file.write(f"\t('{movie[0]}', {movie[1]}, {lang}),\n")

    # Last elem
    for lang in range(1, 4):
        file.write(f"\t('{movies[-1][0]}', {movies[-1][1]}, {lang}),\n")
    file.write(f"\t('{movies[-1][0]}', {movies[-1][1]}, {4});")