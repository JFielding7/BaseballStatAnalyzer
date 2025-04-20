import json
import os.path
from datetime import date, timedelta
from pathlib import Path
import aiohttp
import asyncio

async def fetch_game_details(session, date_folder, game_pk):
    url = f"https://statsapi.mlb.com/api/v1.1/game/{game_pk}/feed/live"

    async with session.get(url) as res:
        game_data = await res.json()

    with open(f"{date_folder}/{game_pk}.json", "w") as game_file:
        json.dump(game_data, game_file)


async def game_data_fetch_tasks(session, games):
    tasks = []

    for date in games['dates']:
        date_folder_path = f"games/{date['date']}"
        Path(date_folder_path).mkdir(exist_ok=True)

        for game in date['games']:
            game_pk = game['gamePk']
            tasks.append(fetch_game_details(session, date_folder_path, game_pk))

    return tasks


async def update_game_files(start, end, game_type):
    url = f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&startDate={start}&endDate={end}&gameTypes={game_type}"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as res:
            games = await res.json()

        Path("games").mkdir(exist_ok=True)
        tasks = await game_data_fetch_tasks(session, games)
        await asyncio.gather(*tasks)


def team_playing(team, game_data):
    teams = game_data['gameData']['teams']
    return teams['away']['teamCode'] == team or teams['home']['teamCode'] == team


def games_on_date(date, team=None):
    date_folder = Path(f"games/{date}")
    if not os.path.exists(date_folder):
        return

    for file in date_folder.iterdir():
        with open(file, "r") as game_file:
            game_data = json.load(game_file)
            if team is None or team_playing(team, game_data):
                yield game_data


def get_game_pk(game):
    return game['gameData']['game']['pk']

def get_game_state(game):
    return game['gameData']['status']['abstractGameState']

def game_plays(game_data):
    return game_data['liveData']['plays']['allPlays']

def get_date(date_str):
    return date(*map(int, date_str.split("-")))


def games_in_date_range(start_date, end_date):
    curr = get_date(start_date)
    end = get_date(end_date)
    games = set()

    while curr <= end:
        for game in games_on_date(curr):
            pk = get_game_pk(game)
            state = get_game_state(game)
            if state == 'Final' and pk not in games:
                yield game
                games.add(pk)
        curr = curr + timedelta(days=1)


if __name__ == "__main__":
    # asyncio.run(update_game_files('2025-04-19', '2025-04-19', 'R'))
    for game in games_in_date_range("2025-03-14", "2025-04-19"):
        pass