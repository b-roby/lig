import json, requests, aiohttp, asyncio

api_key = "RGAPI-14d88b68-a2aa-4699-ae7e-585748779890"

def warning(msg : str):
    print(f"[!] {msg}")

def write_json(new_data, filename):
    with open(filename,'r+') as file:
        file_data = json.load(file)
        file_data["summoners"].append(new_data)
        file.seek(0)
        json.dump(file_data, file, indent = 4)

def read_json(filename):
    with open(filename, 'r') as file:
        data = json.load(file)
        return data

def exists(filename, name):
    with open(filename, 'r') as file:
        file_data = json.load(file)
        for summoner in file_data["summoners"]:
            if summoner["name"] == name:
                return True
        return False
    
def make_endpoint_request(url):
    request_headers = {
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Charset": "application/x-www-form-urlencoded; charset=UTF-8",
        "Origin": "https://developer.riotgames.com",
        "X-Riot-Token": f"{api_key}"
    }

    req = requests.get(url, headers=request_headers)
    return req.json()

async def make_async_request(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 404:
                return None

            return await response.json()