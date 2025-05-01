import tomlkit as toml
from packaging.version import Version

def update_toml_file(team: str, modpack_name: str, latest_global: dict):
    """Update TOML configuration with latest modpack data and increment version."""
    # Load existing TOML
    with open("config.toml", "r") as f:
        toml_data = toml.load(f)
    
    # Calculate new version
    current_version = Version(latest_global["latest_version"])
    new_version = f"{current_version.major}.{current_version.minor}.{current_version.micro + 1}"
    
    # Update core package info
    toml_data["package"].update({
        "namespace": team,
        "name": modpack_name,
        "versionNumber": new_version
    })
    
    # Rebuild dependencies section
    dependencies = {
        dep["dependency"]: dep["latest_version"]
        for dep in latest_global["dependencies"]["latest"]
    }
    
    toml_data["package"]["dependencies"] = dependencies
    
    # Write updated TOML
    with open("config.toml", "w") as f:
        toml.dump(toml_data, f)
