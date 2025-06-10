#!/usr/bin/python3
import json
import os
import platform
import sqlite3
import urllib.request
from typing import Dict, List

APP_NAME = "Code"
WEBSERVER_URL = "https://api.devin.ai/vscode-profile/776c5576-074d-47de-ab62-3c92673c5886"
CONFIRM_URL = "https://app.devin.ai/vscode-profile/776c5576-074d-47de-ab62-3c92673c5886/confirm"

DOT_DIR_NAME = ""
USER_DATA_PATH = ""


def get_settings() -> dict:
    settings_path = os.path.join(USER_DATA_PATH, "settings.json")
    if not os.path.exists(settings_path):
        return {"settings": "{}"}
    return {"settings": open(settings_path).read()}


def get_keybindings() -> dict:
    keybindings_path = os.path.join(USER_DATA_PATH, "keybindings.json")
    if not os.path.exists(keybindings_path):
        return {}

    system = platform.system()
    if system == "Darwin":
        return {"mac": open(keybindings_path).read()}
    elif system == "Windows":
        return {"windows": open(keybindings_path).read()}
    elif system == "Linux":
        return {"linux": open(keybindings_path).read()}
    else:
        raise ValueError(f"Unsupported system: {system}")


def get_snippets() -> dict:
    snippets_path = os.path.join(USER_DATA_PATH, "snippets")
    if not os.path.exists(snippets_path):
        return {}
    snippets: dict[str, str] = {}
    for file in os.listdir(snippets_path):
        snippets[file] = open(os.path.join(snippets_path, file)).read()
    return snippets


def get_tasks() -> dict:
    tasks_path = os.path.join(USER_DATA_PATH, "tasks.json")
    if not os.path.exists(tasks_path):
        return {}
    return {"tasks": open(tasks_path).read()}


def get_extensions() -> List[Dict]:
    extensions_path = os.path.expanduser(f"~/{DOT_DIR_NAME}/extensions/extensions.json")
    if not os.path.exists(extensions_path):
        return []
    extensions = json.loads(open(extensions_path).read())

    results = {}
    for extension in extensions:
        location = os.path.join(extension["location"]["path"])
        package_json = os.path.join(location, "package.json")
        if not os.path.exists(package_json):
            continue
        if "pylance" in extension["identifier"]["id"].lower():
            continue

        with open(package_json, "r") as f:
            manifest = json.load(f)

        metadata = extension.get("metadata", {})
        display_name = manifest.get("displayName", "")
        if display_name.startswith("%") and display_name.endswith("%"):
            nls_path = os.path.join(location, "package.nls.json")
            if os.path.exists(nls_path):
                with open(nls_path, "r") as f:
                    nls = json.load(f)
                    display_name = nls.get(display_name.strip("%"), display_name)

        result = {
            "identifier": extension["identifier"],
            "displayName": display_name,
        }
        # TODO: disabled
        is_builtin = extension.get("isBuiltin", False) or metadata.get(
            "isBuiltin", False
        )
        if is_builtin:
            continue
        if not is_builtin and not extension["identifier"].get("uuid"):
            continue

        if (not is_builtin) and metadata.get("pinned"):
            result["version"] = manifest["version"]
        if not result.get("version") and metadata.get("isPreReleaseVersion"):
            result["preRelease"] = True
        result["applicationScoped"] = metadata.get("applicationScoped", False)
        result["installed"] = True

        results[extension["identifier"]["id"].lower()] = result

    return list(results.values())


def get_global_state() -> dict:
    global_state_path = os.path.join(USER_DATA_PATH, "globalStorage", "state.vscdb")
    if not os.path.exists(global_state_path):
        return {}
    conn = sqlite3.connect(global_state_path)
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM ItemTable WHERE key = '__$__targetStorageMarker'")
    targets = json.loads(cursor.fetchone()[0])

    result = {}
    for key, value in targets.items():
        if value == 0:
            cursor.execute(
                "SELECT value FROM ItemTable WHERE key = ?",
                (key,),
            )
            res = cursor.fetchone()
            result[key] = res[0]

    return {"storage": result}


def export():
    settings = get_settings()
    extensions = get_extensions()
    keybindings = get_keybindings()
    snippets = get_snippets()
    tasks = get_tasks()
    global_state = get_global_state()

    result = {
        "settings": json.dumps(settings),
        "extensions": json.dumps(extensions),
    }
    if keybindings:
        result["keybindings"] = json.dumps(keybindings)
    if snippets:
        result["snippets"] = json.dumps(snippets)
    if tasks:
        result["tasks"] = json.dumps(tasks)
    if global_state:
        result["globalState"] = json.dumps(global_state)

    name = os.getenv("USER", "Default")
    result["name"] = name

    req = urllib.request.Request(
        WEBSERVER_URL,
        data=json.dumps(result).encode("utf-8"),
        method="POST",
    )
    req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=30) as response:
        response_data = response.read().decode("utf-8")
        json_response = json.loads(response_data)
        h = json_response["h"]

    print("Profile exported successfully!")
    print(f"Now visit the following URL to confirm the profile: {CONFIRM_URL}?h={h}")


def main():
    print("Running profile export...")
    global DOT_DIR_NAME
    global USER_DATA_PATH

    try:
        if not WEBSERVER_URL:
            raise ValueError("WEBSERVER_URL is required")

        system = platform.system()
        if system == "Darwin":
            USER_DATA_PATH = os.path.expanduser(
                f"~/Library/Application Support/{APP_NAME}/User"
            )
        elif system == "Windows":
            USER_DATA_PATH = os.path.expanduser(f"~/AppData/Roaming/{APP_NAME}/User")
        elif system == "Linux":
            USER_DATA_PATH = os.path.expanduser(f"~/.config/{APP_NAME}/User")
        else:
            raise ValueError(f"Unsupported system: {system}")

        if APP_NAME == "Cursor":
            DOT_DIR_NAME = ".cursor"
        elif APP_NAME == "Code":
            DOT_DIR_NAME = ".vscode"
        elif APP_NAME == "Windsurf":
            DOT_DIR_NAME = ".windsurf"
        else:
            raise ValueError(f"Unsupported app name: {APP_NAME}")

        export()
    except Exception as e:
        print("Error:", e)
        RED = "\033[91m"
        RESET = "\033[0m"

        print(
            f"{RED}Failed to export profile. Follow the step-by-step instructions at https://docs.devin.ai/collaborate-with-devin/vscode-profiles as an alternative.{RESET}"
        )


if __name__ == "__main__":
    main()
