import os
import json 

PATH = r"./static/songs"


song_list = {}
song_list["songs"] = []
anime_list = [d for d in os.listdir(PATH) if os.path.isdir(os.path.join(PATH,d))]

for anime in anime_list:
    anime_dir = os.path.join(PATH,anime)
    song_files = [os.path.join(anime_dir,f) for f in os.listdir(anime_dir) if os.path.isfile(os.path.join(anime_dir,f))]
    for song in song_files:
        song_list["songs"].append({
            'src': "."+song.replace("\\", "/"),
            'answer': anime.split("-")
        })

print(f"{len(song_list['songs'])} songs found !")
with open(r"./static/songs/songs.json", "w", encoding='utf8') as output:
    json.dump(song_list, output, indent=4, ensure_ascii=False)