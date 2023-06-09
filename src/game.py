from util import make_async_request, api_key, read_json, is_windows, is_linux
from summoner import Summoner
from live_summoner import LiveSummoner

import asyncio, platform

class Game:

    players = []

    if is_windows():
        data_folder = "data/"
        champions_file = data_folder + "champions.json"

    if is_linux():
        data_folder = "/home/blingroby/.virtualenvs/lig/src/data/"
        champions_file = data_folder + "champions.json"

    champions_data = read_json(champions_file)

    async def __search_for_live_game(self, summoner_id, region):
        spectatorv4_url = f"https://{region}.api.riotgames.com/lol/spectator/v4/active-games/by-summoner/{summoner_id}?api_key={api_key}"
        game = await make_async_request(spectatorv4_url)
        return game

    def __init__(self, invoker : LiveSummoner):
        self.players.clear()
        
        game = asyncio.run(self.__search_for_live_game(invoker.id, invoker.region))
        if game == None:
            return None

        for player in game["participants"]:
            summoner = LiveSummoner(player["summonerName"], invoker.region)
            champion_id = player["championId"]
            champion_name = self.champions_data[str(champion_id)]
            summoner.set_champion(champion_name)
            self.players.append(summoner)

            if player["teamId"] == 100:
                summoner.set_team_color(summoner.team_colors.get("blue"))
            elif player["teamId"] == 200:
                summoner.set_team_color(summoner.team_colors.get("red"))
