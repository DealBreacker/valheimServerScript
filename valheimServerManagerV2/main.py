from valheimServerManagerV2.update import *
from toml_editor import *
import subprocess

with open("~/home/dealbreacker/auth_token.json", "r") as f:
    auth_token = json.load(f)


team = "DealBreackers_Assembly" 
modpack_name = "DealBreackers_Haven_Assembly"
latest_local = "current_modlist.json"

api = mods("valheim")

# Get all global mods:
[current_global,latest_global] = mods.global_mods(team, modpack_name, api)

# Get all local mods:
current_local = mods.local_mods(latest_local)

# Compare
[update, add, remove] = mods.compare_versions(current_global, latest_global, current_local)

# Update modlist 
mods.update_mods(update, add, remove)

# Update current_modlist.json (latest_global is new_local)
mods.write_local_mods(latest_global)

# Update toml file
update_toml_file(team, modpack_name, latest_global)

# Build new package
cmd = f"./tcli build"
subprocess.run(cmd)

# Upload new package
cmd = f"./tcli publish --token {auth_token}"
subprocess.run(cmd)
