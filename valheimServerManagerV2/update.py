import requests
from packaging import version
import json
import subprocess

class mods:
    def __init__(self, game):
        api_raw = requests.get(f"https://thunderstore.io/c/{game}/api/v1/package/")
        if api_raw.status_code != 200:
            raise Exception(f"Error {api_raw.status_code}: Could not fetch package list")
        self.api = api_raw.json()

    

    def global_mods(owner, modpack_name, api):
        """
        Check for global mod updates for a specific modpack.
        
        Args:
            owner (str): The owner of the modpack.
            modpack_name (str): The name of the modpack.
        
        Returns:
            dict: A dictionary containing the modpack name, and the version number
            dict: A dictionary containing the current dependency names and versions (of the modpack)
            dict: A dictionary containing the latest dependency names and versions (of the modpack)
        """

        ## ~~~~~~~~~~ GRABBING CURRENT MODPACK NAME AND VERSION ~~~~~~~~~~ ##
        # Find the global modpack by owner and name
        modpack = next((mdpk for mdpk in api if mdpk["owner"] == owner and mdpk["name"] == modpack_name), None)
        if not modpack:
            return f"Modpack '{modpack_name}' by '{owner}' not found"
        
        # Get the latest version
        versions = modpack.get("versions", [])
        if not versions:
            return "No versions found for modpack"
        mdpk_latest = max(versions, key=lambda v: v["version_number"])

        ## ~~~~~~~~~~ GRABBING CURRENT MODPACK DEPENDENCIES  ~~~~~~~~~~ ##
        current_global_dep = []
        for dep in mdpk_latest["dependencies"]:
            parts = dep.split('-')
            if len(parts) < 3:
                continue
            dep_owner = parts[0]
            dep_name = '-'.join(parts[1:-1])
            current_dep_version = parts[-1]
            current_global_dep.append({
                "dependency": f"{dep_owner}-{dep_name}",
                "current_version": current_dep_version
            })

        ## ~~~~~~~~~~ GRABBING LATEST MODPACK DEPENDENCIES ~~~~~~~~~~ ##
            latest_global_dep = []
            for dep in mdpk_latest["dependencies"]:
                parts = dep.split('-')
                if len(parts) < 3:
                    continue
                
                # Extract dependency components
                dep_owner = parts[0]
                dep_name = '-'.join(parts[1:-1])  # Handles names with hyphens
                current_dep_version = parts[-1]

                # Find dependency package in FULL API DATA (not mdpk_latest)
                dep_pkg = next(
                    (pkg for pkg in api  # <- Search through full API data
                    if pkg["owner"] == dep_owner 
                    and pkg["name"] == dep_name),
                    None
                )

                if not dep_pkg:
                    continue

                # Get latest version from dependency package's versions
                latest_dep_version = max(
                    [v["version_number"] for v in dep_pkg["versions"]],
                    key=lambda x: version.parse(x)
                )

                latest_global_dep.append({
                    "dependency": f"{dep_owner}-{dep_name}",
                    "latest_version": latest_dep_version
                })

        return {
        "modpack": f"{owner}-{modpack_name}",
        "latest_version": mdpk_latest["version_number"],
        "dependencies": {
            "current": current_global_dep,
            "latest": latest_global_dep,
            "mdpk_latest": mdpk_latest
        },
    }

    def local_mods(filename):
        """Loads or creates local mods file with proper JSON structure."""
        try:
            f = open(filename)
            current_local = json.load(f)
            return current_local
        except (FileNotFoundError, json.JSONDecodeError):
            # Create file with empty array if missing or invalid
            with open(filename, "w") as f:
                json.dump([], f)
            return []


    def write_local_mods(dir,new_local):
        with open(dir, "w") as f:
            json.dump(new_local, f, indent=4)

    def compare_versions(current_global, latest_global, current_local):
        """
        Compare the current and latest versions of the dependencied
        
        Args:
            current_global (dict): Current global version.
            latest_global (dict): Latest global version.
            current_local (dict): Current local version.
        Returns:
            update (dict): A dictionary containing mods to update.
            add (dict): A dictionary containing mods to add.
            remove (dict): A dictionary containing mods to remove.
        """

        update = []
        add = []
        remove = []

        for dep in current_global:
            if not dep.get("dependency"):
                print(f"Skipping invalid dependency entry: {dep}")  
                continue

            dep_name = dep["dependency"]
            current_version = dep["current_version"]
            latest_version = next((d["latest_version"] for d in latest_global if d["dependency"] == dep_name), None)
            if latest_version and version.parse(current_version) < version.parse(latest_version):
                print(f"Updating {dep_name} from {current_version} to {latest_version}")
                update.append({
                    "mod": dep_name,
                    "current_version": current_version,
                    "latest_version": latest_version
                })
            elif not any(local_dep.get("dependency") == dep_name for local_dep in current_local):
                print(f"Adding {dep_name} with version {latest_version}")
                add.append({
                    "mod": dep_name,
                    "latest_version": latest_version
                })
            else:
                print(f"Dependency {dep_name} is up to date.")
        for dep in current_local:
            if not isinstance(dep, dict) or not dep.get("dependency"):
                print("Skipping invalid local mod entry:", dep)
                continue
            dep_name = dep["dependency"]    
            if not any(global_dep.get("dependency") == dep_name for global_dep in current_global):
                remove.append({
                    "mod": dep_name,
                    "current_version": dep["latest_version"]
                })
        return update, add, remove

    def update_mods(update, add, remove):
        """
        Update the mods based on the comparison results.
        
        Args:
            update (list): List of mods to update.
            add (list): List of mods to add.
            remove (list): List of mods to remove.
        """
        # Update logic here
        for mod in update:
            cmd = f"/home/dealbreacker/valheimServerManager/./tcli install valheim {mod['mod']}-{mod['latest_version']}"
            subprocess.run(cmd, shell = True)        
        for mod in add:
            cmd = f"/home/dealbreacker/valheimServerManager/./tcli install valheim {mod['mod']}-{mod['latest_version']}"
            subprocess.run(cmd, shell = True)
        for mod in remove:
            cmd = f"/home/dealbreacker/valheimServerManager/./tcli uninstall valheim {mod['mod']}"
            subprocess.run(cmd, shell = True)
        if remove:
            subprocess.run("y",shell = True)
        print("Mod list updated successfully.")
            
