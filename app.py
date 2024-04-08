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
UPLOAD_FOLDER = os.path.join(cur_dir, 'temp')
ALLOWED_EXTENSIONS = {'csv'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
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
                flash(f"Executing $edfs {cmd.command} {cmd.file_input} {cmd.arg1} {cmd.arg2}", 'primary')
                response = run_command(cmd, 'mysql')
                if cmd.command == "cat":
                    cat_out = response.output
                    print(cat_out, '\n CAT OUT-------------')
                    if response.status == "danger":
                        flash(response.output, response.status)
                    else:
                        flash(f"Succesfully retreived contents of {cmd.arg1}", response.status)
                        # Handle CAT Output Here
                    print('trying to render')
                    return render_template("database.html", data=html, cat_out=cat_out, analysis_out=analysis_out)
                    
                else:
                    flash(response.output, response.status)

            return redirect(url_for('database_html'))
        
        elif data.get('analyses'):
            analysis_out = run_analyses(data.get('analyses'))
        else:
            pass
    return render_template("database.html", data=html, cat_out=cat_out, analysis_out=analysis_out)


if __name__ == "__main__":
    app.run(debug=True)
