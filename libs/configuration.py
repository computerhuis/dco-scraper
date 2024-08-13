import asyncio
import json
import os
import sys

CONFIGURATION_FILE = 'settings.json'
global settings


# --[ LOAD ]------------------------------------------------------------------------------------------------------------
def init():
    global settings
    settings = None

    if not os.path.isfile(CONFIGURATION_FILE):
        print('No configuration file found, an example  configuration file was created: ', CONFIGURATION_FILE)
        with open(CONFIGURATION_FILE, 'w') as outfile:
            example = {
                "provinces": [
                    {"name": "Drenthe", "url": "/provincie/drenthe"},
                    {"name": "Flevoland", "url": "/provincie/flevoland"},
                    {"name": "Friesland", "url": "/provincie/friesland"},
                    {"name": "Gelderland", "url": "/provincie/gelderland"},
                    {"name": "Groningen", "url": "/provincie/groningen"},
                    {"name": "Limburg", "url": "/provincie/limburg"},
                    {"name": "Noord-Brabant", "url": "/provincie/noord-brabant"},
                    {"name": "Noord-Holland", "url": "/provincie/noord-holland"},
                    {"name": "Overijssel", "url": "/provincie/overijssel"},
                    {"name": "Utrecht", "url": "/provincie/utrecht"},
                    {"name": "Zeeland", "url": "/provincie/zeeland"},
                    {"name": "Zuid-Holland", "url": "/provincie/zuid-holland"}
                ],
                "gemeenten": [
                    {"name": "'s-Hertogenbosch ", "url": "/gemeente/s-hertogenbosch"}
                ],
                "url": "https://postcodebijadres.nl",
                "municipality": None,
                "debug": {
                    "soup": False
                },
            }
            json.dump(example, outfile, sort_keys=True, indent=4)
    else:
        with open(CONFIGURATION_FILE) as json_file:
            settings = json.load(json_file)
            if settings:
                if sys.platform == 'win32':
                    # https://stackoverflow.com/questions/58422817/jupyter-notebook-with-python-3-8-notimplementederror
                    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
