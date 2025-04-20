import json
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


asyncio.run(update_game_files("2025-01-01", "2025-04-17", "R"))
