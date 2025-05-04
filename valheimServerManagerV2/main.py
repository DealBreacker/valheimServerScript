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

# if(update == [] and add == [] and remove == []):
#     print("No changes detected.")
#     exit(0)
# Update modlist 
print("Updating modlist...")
mods.update_mods(update, add, remove)

# Update current_modlist.json (latest_global is new_local)
print("Updating current_modlist.json...")
mods.write_local_mods(latest_local,latest_global)

# Update toml file
print("Updating toml file...")
update_toml_file(team, modpack_name, modpack_latest_ver, latest_global)

# # Upload new package
# print("Uploading package...")
# cmd = f"/home/dealbreacker/valheimServerManager/./tcli publish --token {auth_token['auth_token']}"
# subprocess.run(cmd, shell = True)

# Sync local thunderstore modlist over to server list :)
## This doesn't work yet lol :(
print("Syncing local modlist to server...")
subprocess.run("rsync /home/dealbreacker/.config/ThunderstoreCLI/Profiles/valheim/DefaultProfile/BepInEx/plugins/ /home/dealbreacker/.local/share/Steam/steamapps/common/Valheim\ dedicated\ server/BepInEx/plugins/", shell = True)
print("Done!")