# <span style="color:#4287f5">UEK Schedule Scraper</span>
# What it is
A webpage that scrapes data from [https://planzajec.uek.krakow.pl/](https://planzajec.uek.krakow.pl/) and allows you to see schedule for any group or download **.ICS** calendar 

# How to use
1. Set up virtual environment
   * `py -m venv .venv`
   * `sorce .venv/Scripts/activate`
3. Install libraries
   * `pip install -r requirements.txt`
4. Run the scraper once to prepare the group list:
    * `py get_all_groups.py`
5. Start the Flask app:
    * `py app.py`
6. Open the webpage, enter your user ID, password, and group name.
7. Use one of the two buttons:
    * `Create .ICS` generates the calendar file and downloads it.
    * `Show Calendar` renders a preview table on the page.

# How it works
## 1. config_new.yaml
Template for creation of ```config.yaml```. It is needed for ```get_all_groups.py```
## 2. get_all_groups.py
* One-time usage to get all possible groups(teachers, courses, rooms). **It can take up to 2 minutes.**
* saves everything to ```/groups/all_groups.json```
* in the file you can find dictionary which got this values:
    * ```name``` - that is a field that user will use, 
    * ```id``` - needed for this program to make request
    * ```typ``` - stands for teachers, coursers, rooms(needed to acces the correct calendar)
## 3. scraper.py
This file contains `generate_schedule` the main function `generate_schedule` that accepts 3 parameters:
* group_name - name of the group(like: _ZICSS1-1211_)
* username - student code(_322464_)
* password - student password(_1234_)

It returns 3 values:
* csv_filepath - path to **.csv** file that is later used to display table on the webpage 
* ics_filepath -  path to **.ics** file that is send to user if needed
* error - any kind of errors that may happen during execution
    * Unauthorized: Invalid username or password.
    * No classes found for the specified group. Please check the group name and try again.
    * Unexpected schedule format: missing 'Dzień, godzina' column.

The schedule includes only those clases which typ is `["ćwiczenia", "wykład", "egzamin","laboratorium do wyboru", "laboratorium", "seminarium","konwersatorium do wyboru","konwersatorium"]`
# 4. app.py
## Needed for start of the webpage
The flask app itself. It handles two POST requests:
* download - this creates a url for download of **.ICS** file 
* preview - this sends to webpage columns and rows needed for displaying the table
    
It also saves information about user using `session` -
```userData={"username":session.get("username", ""), "password":session.get("password", ""), "group_name":session.get("group_name", "")}```

Possible errors:
* The generated file is no longer available.
* Please enter a valid Group Name.
