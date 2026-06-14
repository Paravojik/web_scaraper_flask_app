import os
import yaml
import requests
from requests.auth import HTTPBasicAuth
from bs4 import BeautifulSoup
import pandas as pd 
import io
from ics import Calendar, Event
from datetime import datetime
from zoneinfo import ZoneInfo
import json

# with open('config.yaml','r', encoding="utf-8") as f:
#     config=yaml.safe_load(f)
# username=config["credentials"]["username"]
# password=config["credentials"]["password"]
# credentials=HTTPBasicAuth(username, password)


def generate_schedule(group_name,username,password):
    # print(group_name)
    credentials=HTTPBasicAuth(username, password)
    # 252681
    url = f"https://planzajec.uek.krakow.pl/index.php?typ={group_name['typ']}&id={group_name['id']}&okres=2"
    response = requests.get(url,auth = credentials)
    response.encoding = 'utf-8'
    print(response.status_code)
    if response.status_code == 401:
        return None, None, "Unauthorized: Invalid username or password."
    page_dom=BeautifulSoup(response.text, "html.parser")


    group=page_dom.select_one("div.grupa").get_text(strip=True)

    # lectures=page_dom.find_all("th")
    # print(lectures)



    classes_tag=page_dom.select_one("table")
    with open("temp.html", 'w', encoding="utf-8") as f:
        f.write(classes_tag.prettify())
    classes=pd.read_html("temp.html", encoding="UTF-8")[0]
    os.remove("temp.html")
    # print(classes , classes.columns)
    if len(classes)==0:
        return None, None, "No classes found for the specified group. Please check the group name and try again."
    classes = classes.loc[classes["Typ"].isin(["ćwiczenia", "wykład", "egzamin","laboratorium do wyboru", "laboratorium", "seminarium","konwersatorium do wyboru","konwersatorium"])]

    if "Dzień, godzina" not in classes.columns:
        return None, None, "Unexpected schedule format: missing 'Dzień, godzina' column."


    time_parts = classes["Dzień, godzina"].fillna("").astype(str).str.split(r"\s+", n=4, expand=True)
    time_parts = time_parts.reindex(columns=range(5), fill_value="")
    time_parts.columns = ["Day", "Start time", "Hypnen", "End time", "Duration"]
    classes = classes.join(time_parts)

    classes["Duration"] = classes["Duration"].str.extract(r"(\d+)")[0]
    if classes["Duration"].notna().any():
        classes["Duration"] = classes["Duration"].fillna(0).astype(int)
    else:
        classes["Duration"] = 0

    classes = classes.drop(columns=["Dzień, godzina", "Hypnen"], errors="ignore")


    if group_name["typ"]=="S":
        classes["Sala"] = group_name["name"].split(" / ")[-1]
    classes["Sala"] = classes["Sala"].str.replace(r'Win.*', '', regex=True) 

    if not os.path.exists("schedules_ICS"):
        os.mkdir("schedules_ICS")

    ics_calendar = Calendar()
    timezone = ZoneInfo("Europe/Warsaw")

    for _, row in classes.iterrows():
        event = Event()
        event.name = f"{row['Przedmiot']} ({row['Typ']})"
        event.begin = datetime.strptime(f"{row['Termin']} {row['Start time']}", "%Y-%m-%d %H:%M").replace(tzinfo=timezone)
        event.end = datetime.strptime(f"{row['Termin']} {row['End time']}", "%Y-%m-%d %H:%M").replace(tzinfo=timezone)
        event.location = str(row.get("Sala", "") or "")
        event.description = f"Prowadzący: {row.get('Nauczyciel', '')}"
        ics_calendar.events.add(event)

    csv_path = f"schedules/{group}.csv"
    ics_path = f"schedules_ICS/{group}.ics"

    classes.to_csv(csv_path, index_label="ID")
    with open(ics_path, "w", encoding="utf-8") as f:
        f.write(ics_calendar.serialize())

    print(f"Successfully generated {ics_path} with {len(classes)} events!")
    return csv_path, ics_path, False
if __name__ == "__main__":  
    with open('config.yaml','r', encoding="utf-8") as f:
        config=yaml.safe_load(f)
    with open("groups/all_groups.json", 'r', encoding="utf-8") as f:
        all_groups = json.load(f)
    username=config["credentials"]["username"]
    password=config["credentials"]["password"]
    csv_filepath, ics_filepath, error = generate_schedule(all_groups["ZICSS1-1211"], username, password)
    print(csv_filepath, ics_filepath)