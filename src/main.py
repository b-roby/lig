import json, os

with open("data/champions.json", "r") as f:
    json_file = json.load(f)

    for num in json_file:
        champ = json_file[num]
        url = f"https://ddragon.leagueoflegends.com/cdn/img/champion/tiles/{champ}_0.jpg"
        champ = champ.strip(" ")
        os.system(f"curl {url} -o data/champion_tiles/{champ}_tile.jpg")
        