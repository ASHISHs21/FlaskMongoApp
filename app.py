from flask import Flask, render_template, request, redirect, jsonify
from pymongo import MongoClient
import json, os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Connect to MongoDB Atlas
mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
db = client["flask_database"]
collection = db["students"]

# --- 1️⃣ API Route: Return JSON data from backend file ---
@app.route('/api', methods=['GET'])
def get_data():
    try:
        with open("data.json", "r") as file:
            data = json.load(file)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# --- 2️⃣ Frontend Form: Insert data into MongoDB ---
@app.route('/', methods=['GET', 'POST'])
def form_page():
    message = ""
    if request.method == 'POST':
        try:
            name = request.form['name']
            email = request.form['email']
            age = int(request.form['age'])

            # Insert into MongoDB
            collection.insert_one({"name": name, "email": email, "age": age})

            # Redirect to success page
            return redirect('/success')

        except Exception as e:
            message = f"Error: {str(e)}"

    return render_template('form.html', message=message)


# --- 3️⃣ Success Page ---
@app.route('/success')
def success_page():
    return render_template('success.html')


if __name__ == '__main__':
    app.run(debug=True)
