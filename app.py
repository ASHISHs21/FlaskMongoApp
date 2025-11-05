from flask import Flask, render_template, request, redirect, jsonify
from pymongo import MongoClient
import json, os
from dotenv import load_dotenv
import uuid, hashlib

# Load environment variables
load_dotenv()

app = Flask(__name__)

# --- ✅ MongoDB Atlas Connection ---
mongo_uri = os.getenv("MONGO_URI")

if not mongo_uri:
    raise ValueError("❌ MONGO_URI not found in .env file")

try:
    client = MongoClient(mongo_uri)
    db = client["flask_database"]
    collection = db["students"]
    todo_collection = db["todos"]
except Exception as e:
    print("MongoDB Connection Error:", e)
    raise


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

            collection.insert_one({"name": name, "email": email, "age": age})
            return redirect('/success')

        except Exception as e:
            message = f"Error: {str(e)}"

    return render_template('form.html', message=message)


# --- 3️⃣ Success Page ---
@app.route('/success')
def success_page():
    return render_template('success.html')


# --- ✅ 4️⃣ To-Do Page (Frontend Preview Form) ---
@app.route('/todo', methods=['GET'])
def todo_page():
    return render_template('todo.html')


# --- 5️⃣ /submittodoitem Route (POST To-Do items to MongoDB) ---
@app.route('/submittodoitem', methods=['POST'])
def submittodoitem():
    try:
        item_name = request.form.get('itemName')
        item_description = request.form.get('itemDescription')

        if not item_name or not item_description:
            return render_template('todo.html', message="❌ Both fields are required!")

        # Generate UUID and Hash
        item_uuid = str(uuid.uuid4())
        item_hash = hashlib.sha256(item_name.encode()).hexdigest()

        # Store To-Do in MongoDB Atlas
        todo_collection.insert_one({
            "itemName": item_name,
            "itemDescription": item_description,
            "itemUUID": item_uuid,
            "itemHash": item_hash
        })

        return render_template('todo_success.html', itemName=item_name)

    except Exception as e:
        return render_template('todo.html', message=f"Error: {str(e)}")


if __name__ == '__main__':
    app.run(debug=True)
