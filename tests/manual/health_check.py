import os
from dotenv import load_dotenv

root = os.getcwd()
print(f"📂 Project root: {root}")

# Expected directories
expected_dirs = [
    "src",
    os.path.join("src", "fantasy_ai"),
    os.path.join("src", "fantasy_ai", "api"),
    os.path.join("src", "fantasy_ai", "utils"),
]

print("\n📁 Checking required directories:")
for d in expected_dirs:
    if os.path.isdir(d):
        print(f" - {d:35} ✅")
    else:
        print(f" - {d:35} ❌ MISSING")

# __init__.py files
init_files = [
    os.path.join("src", "fantasy_ai", "__init__.py"),
    os.path.join("src", "fantasy_ai", "api", "__init__.py"),
    os.path.join("src", "fantasy_ai", "utils", "__init__.py"),
]

print("\n📄 Checking __init__.py files:")
for f in init_files:
    if os.path.isfile(f):
        print(f" - {f:35} ✅")
    else:
        print(f" - {f:35} ❌ MISSING")

# Check .env & LEAGUE_ID
print("\n🔍 Checking .env file and LEAGUE_ID:")
env_path = os.path.join(root, ".env")
if os.path.isfile(env_path):
    load_dotenv(env_path)
    league_id = os.getenv("LEAGUE_ID")
    if league_id:
        print(f" - .env found, LEAGUE_ID = {league_id} ✅")
    else:
        print(" - .env found but LEAGUE_ID is missing/empty ❌")
else:
    print(" - .env file ❌ MISSING")

print("\n✅ Health check complete.")