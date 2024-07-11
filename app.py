import requests
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import json
from werkzeug.security import check_password_hash

app = Flask(__name__)
app.secret_key = 'Monasturev08122002'
json_file_path = 'host.json'


with open(json_file_path, 'r') as file:
    host_data = json.load(file)

HOST = host_data['host']
logs_url = f"http://{HOST}/archive_logs"

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


class User(UserMixin):
    def __init__(self, id):
        self.id = id


@login_manager.user_loader
def load_user(user_id):
    return User(user_id)


def read_data():
    with open('data.json', 'r') as file:
        data = json.load(file)
    return data


def write_data(data):
    with open('data.json', 'w') as file:
        json.dump(data, file, indent=4)


@app.route('/')
@login_required
def index():
    data = read_data()
    return render_template('index.html', data=data, link=logs_url, HOST=HOST)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        with open('password.json', 'r') as file:
            login_data = json.load(file)
        # For simplicity, we use hardcoded username and password
        # In a real application, use a database and hashed passwords
        if username == login_data['login'] and check_password_hash(login_data['password'], password):
            user = User(username)
            login_user(user)
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error="Invalid username or password")
    return render_template('login.html')


@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return redirect("/login")

@app.route('/reload', methods=['POST'])
def reload():
    # Add your reload logic here
    return jsonify({"status": "reloaded"})

@app.route('/download_logs', methods=['POST'])
def download_logs():

    return jsonify({"status": "downloaded"})

@app.route('/host', methods=['POST'])
def host():
    global HOST
    host_data = request.json
    if not host_data:
        return jsonify({"status": "failed", "error": "No data received"}), 400

    with open('host.json', 'w') as file:
        json.dump(host_data, file, indent=4)
    HOST = host_data['host']
    return jsonify({"status": "host_data_applyed: host_data"})


@app.route('/send', methods=['POST'])
def send():
    try:
        data = request.json
        if not data:
            return jsonify({"status": "failed", "error": "No data received"}), 400

        # Debugging output to check received data
        print("Received data:", data)

        # Example URL, replace with actual API endpoint
        external_api_url = f'http://{HOST}/update_data'

        try:
            response = requests.post(external_api_url, json=data)
            if response.status_code == 200:
                write_data(data)
                return jsonify({"status": "data_sent", "data": data})
            else:
                return jsonify({"status": "failed", "error": response.text}), response.status_code
        except requests.RequestException as e:
            return jsonify({"status": "failed", "error": str(e)}), 500

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return jsonify({"status": "failed", "error": str(e)}), 500


@app.route('/status', methods=['GET'])
def status():
    try:
        # Example URL, replace with actual API endpoint
        external_api_url = f'http://{HOST}/status'

        response = requests.get(external_api_url)

        if response.status_code == 200:

            status_data = response.json().get('status', False)
            # Предполагаем, что булевое значение хранится под ключом 'result'
            return jsonify({"status": status_data})

        else:
            return jsonify({"status": False}), response.status_code
    except requests.RequestException as e:
        return jsonify({"status": False, "error": str(e)}), 500

if __name__ == '__main__':
    context = ('fullchain.pem', 'privkey.pem')

    app.run(host='0.0.0.0', port=443, ssl_context=context)




"""
#registration
from werkzeug.security import generate_password_hash

@app.route('/register', methods=['POST'])
def register():
    # Assuming you receive the password in a form or JSON data
    login_data = request.get_json()
    print(login_data['password'])
    # Hash the password before saving it
    hashed_password = generate_password_hash(login_data['password'])
    print(hashed_password)
    # Save hashed_password in your database
    # Example: user.password = hashed_password
    data_login={
        "login":login_data['login'],
        "password":hashed_password
    }

    with open('password.json', 'w') as file:
        json.dump(data_login, file, indent=4)
    return 'User registered successfully'
"""