from update import mods
import json
from toml_editor import update_toml_file
import subprocess

with open("/home/dealbreacker/auth_token.json", "r") as f:
    auth_token = json.load(f)


team = "DealBreackers_Assembly" 
modpack_name = "DealBreackers_Haven_Assembly"
latest_local = "/home/dealbreacker/valheimServerManager/valheimServerManagerV2/current_modlist.json"

api = mods("valheim").api

# Get all global mods:
print("Grabbing global mods...")
global_data = mods.global_mods(team, modpack_name, api)
current_global = global_data["dependencies"]["current"]
latest_global = global_data["dependencies"]["latest"]
modpack_latest_ver = global_data["latest_version"]

# Get all local mods:
print("Grabbing local mods...")
current_local = mods.local_mods(latest_local)

# Compare
print("Comparing mods...")
[update, add, remove] = mods.compare_versions(current_global, latest_global, current_local)

# Update modlist 
print("Updating modlist...")
mods.update_mods(update, add, remove)

# Update current_modlist.json (latest_global is new_local)
print("Updating current_modlist.json...")
mods.write_local_mods(latest_local,latest_global)

# Update toml file
print("Updating toml file...")
update_toml_file(team, modpack_name, modpack_latest_ver, latest_global)

# Build new package
cmd = f"/home/dealbreacker/valheimServerManager/./tcli build"
subprocess.run(cmd, shell = True)

# # Upload new package
# cmd = f"./tcli publish --token {auth_token}"
# subprocess.run(cmd)
