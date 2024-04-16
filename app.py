import sys
import os
from flask import Flask, render_template, request, redirect, flash, url_for
sys.path.append(os.path.relpath('../src/lib/edfs/'))
from helper import *
from requests.exceptions import ConnectionError
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

cur_dir = os.path.dirname(os.path.realpath(__file__))

app = Flask(__name__)
app.secret_key = b'Placeholder'

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/database.html", methods=('GET', 'POST'))
def database_html():
    analysis_out = ""
    html="Placeholder"
    cat_out = ""
    if request.method == 'POST':
        data = request.form.to_dict()
        if data.get('command'):
            file = request.files.get('file_input')
            data['file_input'] = file
            cmd = validate_input(data, file)
            if cmd.error:
                flash(cmd.error, 'danger')
            else:
                flash(f"{cmd.operation}", 'primary')
                analysis_out = run_analyses(cmd)
        print(analysis_out)
    return render_template("database.html", data=html, cat_output=cat_out, analyses_output=analysis_out)

@app.route('/route/<callsign>')
def get_flight_details(callsign):
    # Construct the query based on callsign
    print("HERE")
    query = f"SELECT * FROM flight_data WHERE callsign = '{callsign}'"
    response = requests.post("http://127.0.0.1:8090/database/query", json={"partitionKey":callsign, "tableName": "flight_data", "query": query})
    flight_details = response.json()
    return render_template('flight_details.html', flight_details=flight_details)

if __name__ == "__main__":
    app.run(debug=True)
