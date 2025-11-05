from flask import Flask, render_template, request, redirect, jsonify
from pymongo import MongoClient
import json, os
from dotenv import load_dotenv
import uuid, hashlib

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Connect to MongoDB Atlas
mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
db = client["flask_database"]
collection = db["students"]
todo_collection = db["todos"]

# --- 1️⃣ API Route: Return JSON data from backend file ---
@app.route('/api', methods=['GET'])
def get_data():
    try:
        with open("data.json", "r") as file:
            data = json.load(file)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# --- 2️⃣ Frontend Form: Insert user data into MongoDB ---
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

            return redirect('/success')
        except Exception as e:
            message = f"Error: {str(e)}"

    return render_template('form.html', message=message)


# --- 3️⃣ Success Page ---
@app.route('/success')
def success_page():
    return render_template('success.html')


# --- 4️⃣ New Backend Route: /submittodoitem (Master_2 feature) ---
@app.route('/submittodoitem', methods=['POST'])
def submittodoitem():
    try:
        item_name = request.form.get('itemName')
        item_description = request.form.get('itemDescription')

        if not item_name or not item_description:
            return jsonify({"error": "Both itemName and itemDescription are required"}), 400

        # Generate UUID and Hash
        item_uuid = str(uuid.uuid4())
        item_hash = hashlib.sha256(item_name.encode()).hexdigest()

        # Store in MongoDB
        todo_collection.insert_one({
            "itemName": item_name,
            "itemDescription": item_description,
            "itemUUID": item_uuid,
            "itemHash": item_hash
        })

        return jsonify({
            "message": "To-Do item submitted successfully!",
            "itemName": item_name,
            "itemDescription": item_description,
            "itemUUID": item_uuid,
            "itemHash": item_hash
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
