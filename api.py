from flask import Flask, request, jsonify
import csv
import os

app = Flask(__name__)

CSV_FILE = "data.csv"

# Ensure CSV file exists with headers
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Parent Name", "Child Name", "Phone", "Email", "DOB", "Class", "Occupation", "Address"])

@app.route("/submit", methods=["POST"])
def submit_form():
    try:
        data = request.json
        with open(CSV_FILE, mode="a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([
                data["parent_name"],
                data["child_name"],
                data["phone"],
                data["email"],
                data["dob"],
                data["class"],
                data["occupation"],
                data["address"]
            ])
        return jsonify({"message": "Form submitted successfully!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 50
def home():
    return "Server is running!"

@app.route("/submit", methods=["POST"])
def submit_form():
    return "Form received!"  # (Update with CSV saving logic)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

