import json
import os
from sly_sdk.sly import WebPyApplication


def find_gui_dir():
    if not os.path.exists("config.json"):
        return ""
    with open("config.json") as f:
        config = json.load(f)
        return config.get("gui_folder_path", "")


if __name__ == "__main__":
    import gui

    WebPyApplication.render(
        layout=gui.layout, dir=find_gui_dir(), requirements_path="requirements.txt"
    )
