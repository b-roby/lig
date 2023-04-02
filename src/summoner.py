import json, asyncio, time
from .util import make_async_request, api_key

def warning(msg : str):
    print(f"[!] {msg}")

def write_json(summoner_data, filename):
    with open(filename,'r+') as file:
        file_data = json.load(file)
        file_data["summoners"].append(summoner_data)
        file.seek(0)
        json.dump(file_data, file, indent=4)
        file.truncate()
    
# def delete_json()
def read_json(filename):
    with open(filename, 'r') as file:
        data = json.load(file)
        return data
        
class Summoner:

    region = {'eune': 'eun1', 'euw': 'euw1', 'na': 'na1'}
    data_folder = "./data/"   
    summoners_file = data_folder + "summoners.json"

    id = ""
    name = ""
    region = ""
    level = 0

    rank_soloq = ""
    tier_soloq = 0
    division_soloq = "Unranked"
    lp_soloq = 0
    wins_soloq = 0
    losses_soloq = 0

    rank_flex = "" 
    tier_flex = 0
    division_flex = "Unranked"
    lp_flex = 0
    wins_flex = 0
    losses_flex = 0

    time_gathered = 0
    
    tier_color_soloq = "gray"
    tier_color_flex = "gray"

    rank_colors = {"unranked" : "gray", "irn": "#a19d94", "bronze": "#CD7F32", "silver": "#C0C0C0", 
                       "gold": "#FFD700", "platinum": "#d0f6ff", "diamond": "#437ff9", "master": "#710193", 
                       "grandmaster": "#D73502", "challenger": "#6082B6"}

    #TODO MAKE IT MORE EFFICIENT
    def is_stored(self, name):
        with open(self.summoners_file, 'r') as file:
            file_data = json.load(file)
            for summoner in file_data["summoners"]:
                if summoner["name"] == name:
                    return True
            return False

    def create_summoner(self):
        summoner_dict = {
            'name': self.name,
            'region': self.region,
            'level': self.level,
            'id': self.id,
            'soloq': {
                'rank': self.division_soloq,
                'lp': self.lp_soloq,
                'wins': self.wins_soloq,
                'losses': self.losses_soloq
            },
            'flex': {
                'rank': self.division_flex,
                'lp': self.lp_flex,
                'wins': self.wins_flex,
                'losses': self.losses_flex,
            },
            'time_gathered': self.time_gathered,
            'tier_color_soloq': self.tier_color_soloq,
            'tier_color_flex': self.tier_color_flex
        }
        write_json(summoner_dict, self.summoners_file)

    def __search_for_summoner_file(self, summoner_name):
        data = read_json(self.summoners_file)
        summoners = data["summoners"]

        for summoner in summoners:
            if summoner["name"] == summoner_name:
                return summoner
            
        return None
            
    def deserialize(self, summoner_name):
        summoner = self.__search_for_summoner_file(summoner_name)
        
        self.name = summoner["name"]
        self.region = summoner["region"]

        self.id = summoner["id"]
        self.level = summoner["level"]

        rank_soloq = summoner["soloq"]["rank"]
        self.division_soloq = rank_soloq
        self.lp_soloq = summoner["soloq"]["lp"]
        self.wins_soloq = summoner["soloq"]["wins"]
        self.losses_soloq = summoner["soloq"]["losses"]

        rank_flex = summoner["flex"]["rank"]
        self.division_flex = rank_flex
        self.lp_flex = summoner["flex"]["lp"]
        self.wins_flex = summoner["flex"]["wins"]
        self.losses_flex = summoner["flex"]["losses"]

        self.time_gathered = summoner["time_gathered"]
        self.tier_color_soloq = self.rank_colors.get(rank_soloq.split(" ")[0].lower())
        self.tier_color_flex = self.rank_colors.get(rank_flex.split(" ")[0].lower())
        
    def delete_summoner(self, summoner_name):
        data = read_json(self.summoners_file)
        summoners = data["summoners"]

        i = 0
        for summoner in summoners:
            if summoner["name"] == summoner_name:
                summoners.pop(i)
                break
            i += 1

        data["summoners"] = summoners

        with open(self.summoners_file, "r+") as file:
            file.seek(0)
            json.dump(data, file, indent=4)
            file.truncate()

    def should_serialize(self, summoner_name):
        summoner = self.__search_for_summoner_file(summoner_name)
        if summoner == None:
            return True
        return False

    async def __search_for_summoner(self, summoner_name, region):
        summonerv4_url = f"https://{region}.api.riotgames.com/lol/summoner/v4/summoners/by-name/{summoner_name}?api_key={api_key}"
        summoner = await make_async_request(summonerv4_url)
        return summoner
            
    async def __search_for_info(self, summoner_id, region):
        leaguev4_url = f"https://{region}.api.riotgames.com/lol/league/v4/entries/by-summoner/{summoner_id}?api_key={api_key}"
        info = await make_async_request(leaguev4_url)
        return info

    def __init__(self, name, region):
        summoner = self.__search_for_summoner_file(name)
        time_gathered = 0
        current_time = 0
        
        if summoner != None:
            time_gathered = summoner["time_gathered"]
        
        current_time = round(time.time())
        update_delay = 60 * 5

        if summoner != None and time_gathered + update_delay >= current_time:
            self.deserialize(name)
            return
        
        self.name = name
        self.region = region

        summoner = asyncio.run(self.__search_for_summoner(self.name, self.region))
        if summoner is None:
            return
        
        self.id = summoner["id"]
        self.level = summoner["summonerLevel"]

        info = asyncio.run(self.__search_for_info(self.id, self.region))

        self.division_soloq = "unranked"
        self.division_flex = "unranked"

        try:
            if "TFT" in info[0]["queueType"]:
                info.pop(0)
        except IndexError:
            pass

        try:
            flex = info[1]
            self.tier_flex = flex["tier"]
            self.rank_flex = flex["rank"]
            self.division_flex = f"{self.tier_flex.lower().capitalize()} {self.rank_flex}"
            self.tier_color_flex = self.rank_colors.get(self.tier_flex.lower())
            self.lp_flex = flex["leaguePoints"]
            self.wins_flex = flex["wins"]
            self.losses_flex = flex["losses"]
        except IndexError:
            pass

        try:
            soloq = info[0]  
            self.tier_soloq = soloq["tier"]
            self.rank_soloq = soloq["rank"]
            self.division_soloq = f"{self.tier_soloq.lower().capitalize()} {self.rank_soloq}"
            self.tier_color_soloq = self.rank_colors.get(self.tier_soloq.lower())
            self.lp_soloq = soloq["leaguePoints"]
            self.wins_soloq = soloq["wins"]
            self.losses_soloq = soloq["losses"]
        except IndexError:
            pass

        self.time_gathered = round(time.time())

        if self.__search_for_summoner_file(name) != None:
            self.delete_summoner(name)

        self.create_summoner()