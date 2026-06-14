from flask import Flask, render_template, request, send_file, flash, session, url_for
import os
import re
import pandas as pd
from scraper import generate_schedule
if os.path.exists("groups/all_groups.json"):
    import json
    with open("groups/all_groups.json", 'r', encoding="utf-8") as f:
        all_groups = json.load(f)
else:
    raise FileNotFoundError("The file 'groups/all_groups.json' does not exist. Please run 'get_all_groups.py' first to generate it.")
app = Flask(__name__)
app.secret_key = "super_secret_key_for_flash_messages" #Why :(


@app.route("/download/<path:filename>")
def download_file(filename):
    file_path = os.path.join("schedules_ICS", filename)
    print(file_path)
    if not os.path.exists(file_path):
        flash("The generated file is no longer available.")
        userData={"username":session.get("username", ""), "password":session.get("password", ""), "group_name":session.get("group_name", "")}
        return render_template("index.html", groups=all_groups, userData=userData)
    return send_file(file_path, as_attachment=True)

@app.route("/", methods=["GET", "POST"])
def index():
    userData={"username":session.get("username", ""), "password":session.get("password", ""), "group_name":session.get("group_name", "")}
    if request.method == "POST":
        group_name=request.form.get("group_name").split(" / ")[-1]
        username=request.form.get("user_id")
        password=request.form.get("password")
        action = request.form.get("action", "download")

        session["group_name"] = group_name
        session["username"] = username
        session["password"] = password
        
        if not group_name or group_name not in all_groups.keys():
            flash("Please enter a valid Group Name.")
            userData={"username":session.get("username", ""), "password":session.get("password", ""), "group_name":session.get("group_name", "")}
            return render_template("index.html", groups=all_groups, userData=userData)

        # Run the scraper
        print(f"Generating schedule for group: {group_name}")
        csv_filepath, ics_filepath, error = generate_schedule(all_groups[group_name], username, password)
        print(csv_filepath, ics_filepath, error)
        if error:
            flash(error)
            userData={"username":session.get("username", ""), "password":session.get("password", ""), "group_name":session.get("group_name", "")}

            return render_template("index.html", groups=all_groups, userData=userData)

        if csv_filepath and os.path.exists(csv_filepath):
            if action == "download":
                
                download_url = url_for("download_file", filename=os.path.basename(ics_filepath))
                userData={"username":session.get("username", ""), "password":session.get("password", ""), "group_name":session.get("group_name", "")}

                return render_template("index.html", groups=all_groups, userData=userData, download_url=download_url)
            elif action == "preview":
                preview_df = pd.read_csv(csv_filepath)
                userData={"username":session.get("username", ""), "password":session.get("password", ""), "group_name":session.get("group_name", "")}
                return render_template(
                    "index.html",
                    groups=all_groups,
                    userData=userData,
                    preview_columns=preview_df.columns.tolist(),
                    preview_rows=preview_df.to_dict(orient="records"),
                )

    return render_template("index.html", groups=all_groups, userData=userData)


if __name__ == "__main__":
    app.run(debug=True) 