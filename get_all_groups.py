import re

from bs4 import BeautifulSoup
import requests
from requests.auth import HTTPBasicAuth
import yaml
import os
import json

def get_all_groups(credentials):
    all_groups={}
    url= "https://planzajec.uek.krakow.pl"
    response = requests.get(url, auth=credentials)
    response.encoding = 'utf-8'
    page_dom = BeautifulSoup(response.text, "html.parser")
    courses = page_dom.find_all("a")[1:-1]
    # print(courses)
    for course in courses:
        res = requests.get(f"https://planzajec.uek.krakow.pl/{course['href']}", auth=credentials )
        res.encoding = 'utf-8'
        course_page = BeautifulSoup(res.text, "html.parser")
        groups = course_page.find_all("a")
        for group in groups[1:-1]:
            all_groups[group.get_text(strip=True)]={"name": f"{course.get_text(strip=True)} / {group.get_text(strip=True)}","typ": re.search(r'typ=(\w)', group['href']).group(1), "id": re.search(r'id=(\d+)', group['href']).group(1)}
    if not os.path.exists("groups"):
        os.mkdir("groups")
    with open("groups/all_groups.json", 'w', encoding="utf-8") as f:
        json.dump(all_groups, f, ensure_ascii=False, indent=4)
    return all_groups

if __name__ == "__main__":
    with open('config.yaml','r', encoding="utf-8") as f:
        config=yaml.safe_load(f)
    username=config["credentials"]["username"]
    password=config["credentials"]["password"]
    credentials=HTTPBasicAuth(username, password)
    groups = get_all_groups(credentials)
    print(groups)
