import gzip
import json
import os
import requests
from xml.etree import ElementTree as ET

# Constants
EPG_URL = "https://epgshare01.online/epgshare01/epg_ripper_US1.xml.gz"
OUTPUT_JSON = "epg_ripper_US1.json"

def fetch_and_unzip_epg():
    """Fetch and unzip the EPG file."""
    try:
        print("Fetching the EPG file...")
        response = requests.get(EPG_URL, stream=True)
        response.raise_for_status()
        
        # Save the gzipped file
        gz_path = "epg_ripper_US1.xml.gz"
        with open(gz_path, "wb") as f:
            f.write(response.content)
        print("EPG file downloaded.")

        # Unzip the file
        print("Unzipping the EPG file...")
        with gzip.open(gz_path, "rt", encoding="utf-8") as gz_file:
            xml_data = gz_file.read()

        # Cleanup
        os.remove(gz_path)
        print("EPG file unzipped successfully.")
        return xml_data

    except Exception as e:
        print(f"Error fetching or unzipping EPG: {e}")
        return None

def convert_xml_to_json(xml_data):
    """Convert XML data to JSON format."""
    try:
        # Determine the output path in the same directory as the script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_json = os.path.join(script_dir, "epg_ripper_US1.json")
        
        print("Converting XML to JSON...")
        root = ET.fromstring(xml_data)
        epg_data = {"channels": []}

        # Extract channels
        for channel in root.findall("channel"):
            channel_id = channel.get("id")
            display_name = channel.findtext("display-name", default="Unknown Channel")
            icon = channel.find("icon").get("src") if channel.find("icon") is not None else None

            # Manually filter programmes for the current channel
            programmes = []
            for programme in root.findall("programme"):
                if programme.get("channel") == channel_id:
                    title = programme.findtext("title", default="Unknown Show")
                    start_time = programme.get("start")
                    stop_time = programme.get("stop")
                    desc = programme.findtext("desc", default="No Description")

                    programmes.append({
                        "title": title,
                        "start": start_time,
                        "stop": stop_time,
                        "description": desc
                    })

            epg_data["channels"].append({
                "id": channel_id,
                "display_name": display_name,
                "icon": icon,
                "programmes": programmes
            })

        # Save JSON data to a file in the same directory as the script
        with open(output_json, "w", encoding="utf-8") as json_file:
            json.dump(epg_data, json_file, ensure_ascii=False, indent=4)
        print(f"JSON file saved as {output_json}.")

    except Exception as e:
        print(f"Error converting XML to JSON: {e}")

def main():
    xml_data = fetch_and_unzip_epg()
    if xml_data:
        convert_xml_to_json(xml_data)

if __name__ == "__main__":
    main()
