from flask import Flask, render_template, jsonify, request
import subprocess
import json

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/fetch_trends', methods=['POST'])
def trends():
    try:
        # Get username and password from the request
        username = request.form['username']
        password = request.form['password']
        print(password)
        # Pass username and password to the trends fetching function
        trends_data = subprocess.run(['python', 'trends.py', username, password], capture_output=True, text=True, check=True)
        data = json.loads(trends_data.stdout)  # Safely parse JSON
        return jsonify(data)
    except subprocess.CalledProcessError as e:
        print(f"Error fetching trends: {e}")
        return jsonify({"error": "Error fetching trends"}), 500
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return jsonify({"error": "Error decoding JSON"}), 500

if __name__ == '__main__':
    app.run(debug=True)
