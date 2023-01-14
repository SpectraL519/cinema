import pandas as pd
import numpy as np
from datetime import datetime, timedelta



lengths = [146, 101, 100, 150, 150, 115, 135, 145, 125, 130, 193]
movies = range(len(lengths))
langs = range(1, 5)
rooms = range(1, 12)

with open("./docs/schedule.txt", 'w') as file:
    file.write("INSERT INTO Schedule(movie_id, room_id, start_time, s_taken) VALUES\n")


    start = datetime.now()
    for plus in range(60):
        opening = (start + timedelta(days=plus)).replace(hour=12, minute=0, second=0, microsecond=0)
        for movie in movies:
            current = opening
            delta = 30
            while delta <= lengths[movie]: delta += 30

            for lang in langs:
                if plus == 59 and movie == movies[-1] and lang == langs[-1]:
                    file.write(f"\t({(movie * 4) + lang}, {rooms[movie]}, '{current}', 0);")
                else:
                    file.write(f"\t({(movie * 4) + lang}, {rooms[movie]}, '{current}', 0),\n")
                    current = current + timedelta(minutes=delta)