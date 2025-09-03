import requests, json

week = 3
url = f"https://api.sleeper.com/projections/nfl/2025/{week}?season_type=regular&position[]=DEF&position[]=FLEX&position[]=K&position[]=QB&position[]=RB&position[]=SUPER_FLEX&position[]=TE&position[]=WR&order_by=ppr"

resp = requests.get(url)
resp.raise_for_status()
data = resp.json()

print(f"Type: {type(data)}, length: {len(data)}")
if isinstance(data, list) and data:
    print("Sample keys:", list(data[0].keys()))
    print(json.dumps(data[0], indent=2)[:500])