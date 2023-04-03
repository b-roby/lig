from summoner import Summoner

class LiveSummoner(Summoner):

    live_champion = "Not playing"
    live_champion_raw = "NotPlaying"

    team_colors = {"blue": "#0047AB", "red": "#D70040"}
    team_color = "None"

    def __init__(self, name, region):
        super(LiveSummoner, self).__init__(name, region)

    def set_champion(self, champion_name):
        self.live_champion = champion_name
        self.live_champion_raw = champion_name.replace(" ", "")
        self.live_champion_raw = self.live_champion_raw.replace("'", "")

    def set_team_color(self, team_color):
        self.team_color = team_color