import json

def get_settings_data():
    # Path to your settings.json file
    settings_file = 'settings.json'

    # Load the JSON data from the file
    with open(settings_file, 'r') as file:
        return json.load(file)
