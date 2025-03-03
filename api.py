from flask import Flask, request, jsonify
from flask_cors import CORS
import csv
import boto3
import os

app = Flask(__name__)
CORS(app)

# File and S3 configurations
CSV_FILE = "enquiry_data.csv"
AWS_ACCESS_KEY = "AKIA5CSKK24EK2NCIJPK"
AWS_SECRET_KEY = "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"
S3_BUCKET_NAME = "enquiryform01"
S3_FILE_NAME = "enquiry_data.csv"

# Initialize S3 client
s3 = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY
)

# Ensure CSV file exists with headers
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Parent Name", "Child Name", "Phone", "Email", "DOB", "Class", "Occupation", "Address"])

def upload_to_s3():
    """Uploads the updated CSV file to S3"""
    try:
        s3.upload_file(CSV_FILE, S3_BUCKET_NAME, S3_FILE_NAME)
        print("File uploaded to S3 successfully!")
        return True
    except Exception as e:
        print(f"Error uploading to S3: {e}")
        return False

@app.route("/submit", methods=["POST"])
def submit_form():
    """Save form data to CSV and upload it to S3"""
    try:
        data = request.json

        # Append data to CSV file
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
        
        print("Data written to CSV successfully!")

        # Upload CSV to S3
        success = upload_to_s3()

        if success:
            return jsonify({"message": "Form submitted and CSV updated to S3!"}), 200
        else:
            return jsonify({"error": "Failed to upload CSV to S3"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
