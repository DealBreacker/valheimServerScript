import requests
from packaging import version
import os



def check_latst_modpack_updates(owner, modpack_name, local_dir, game="valheim"):
    # Download all packages for the games from ThunderstoreAPI
    url = f"https://thunderstore.io/c/{game}/api/v1/package/"
    response = requests.get(url)
    if response.status_code != 200:
        return f"Error {response.status_code}: Could not fetch package list"
    packages = response.json()

    # Find the global modpack by owner and name
    modpack = next((p for p in packages if p["owner"] == owner and p["name"] == modpack_name), None)
    if not modpack:
        return f"Modpack '{modpack_name}' by '{owner}' not found"
    
    # Get the latest version
    versions = modpack.get("versions", [])
    if not versions:
        return "No versions found for modpack"
    latest_version = max(versions, key=lambda v: v["version_number"])

    # Check the global and local dependencies for updates
    global_updates = []
    local_updates = []

    for dep in latest_version["dependencies"]:
        parts = dep.split('-')
        if len(parts) < 3:
            continue
        dep_owner = parts[0]
        dep_name = '-'.join(parts[1:-1])
        current_global_version = parts[-1]

        # Find the dependency package in the full list
        dep_pkg = next((p for p in packages if p["owner"] == dep_owner and p["name"] == dep_name), None)
        if not dep_pkg or not dep_pkg.get("versions"):
            continue
        
        # Find the most recent version of the dependency
        latest_dep_version = max(
            (v["version_number"] for v in dep_pkg["versions"]),
            key=lambda x: version.parse(x)
        )

        # Compare versions
        # If the latest version is greater than the current version, add to updates
        if version.parse(latest_dep_version) > version.parse(current_global_version):
            global_updates.append({
                "mod": f"{dep_owner}-{dep_name}",
                "current_version": current_global_version,
                "latest_version": latest_dep_version
            })
        
        # Check local dependencies
        local_mod_path = os.path.join(local_dir, f"{dep_name}")
        if os.path.exists(local_mod_path):
            with open(os.path.join(local_mod_path, "version.txt"), "r") as f:
                current_local_version = f.read().strip()
            
            if version.parse(latest_dep_version) > version.parse(current_local_version):
                local_updates.append({
                    "mod": f"{dep_owner}-{dep_name}",
                    "current_version": current_local_version,
                    "latest_version": latest_dep_version
                })

    return {
        "modpack": f"{owner}-{modpack_name}",
        "latest_version": latest_version["version_number"],
        "outdated_mods_global": global_updates,
        "outdated_mods_local": local_updates,
        "total_mods": len(latest_version["dependencies"])
    }

def update_mods_with_tcli(outdated_mods, dir):
    for mod in outdated_mods:
        mod_id = f"{mod['mod']}-{mod['latest_version']}"
        cmd = ["./tcli", "install", "valheim", mod_id]
    if profile:
        cmd.extend(["--profile", profile])
    print("Running:", " ".join(cmd))
    subprocess.run(cmd)