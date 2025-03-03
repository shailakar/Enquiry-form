from flask import Flask, request, jsonify
from flask_cors import CORS
import csv
import boto3
import os

app = Flask(__name__)
CORS(app)

# File and AWS S3 Configurations
CSV_FILE = "enquiry_data.csv"
AWS_ACCESS_KEY = "AKIA5CSKK24EK2NCIJPK"  # Replace with your AWS Access Key
AWS_SECRET_KEY = "tSwivYku7hn62HUoIq7Ci9akczBc97bmjZaMgR7Q"  # Replace with your AWS Secret Key
S3_BUCKET_NAME = "enquiryform01"  # Your S3 bucket name
S3_FILE_NAME = "enquiry_data.csv"  # File name in S3

# Initialize S3 Client
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
    """Uploads the updated CSV file to S3 (Private)"""
    try:
        s3.upload_file(
            CSV_FILE,  # Local file
            S3_BUCKET_NAME,  # S3 bucket name
            S3_FILE_NAME,  # S3 file name
            ExtraArgs={"ContentType": "text/csv"}  # Set correct content type
        )
        print(f"File uploaded to S3: {S3_FILE_NAME}")
        return True
    except Exception as e:
        print(f"Error uploading to S3: {e}")
        return False

def generate_presigned_url():
    """Generates a temporary secure URL to access the CSV file"""
    try:
        url = s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": S3_BUCKET_NAME, "Key": S3_FILE_NAME},
            ExpiresIn=3600  # URL valid for 1 hour
        )
        return url
    except Exception as e:
        print(f"Error generating presigned URL: {e}")
        return None

@app.route("/")
def home():
    return "Server is running!"

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

        # Upload CSV to S3 (private)
        success = upload_to_s3()

        if success:
            return jsonify({"message": "Form submitted!"}), 200
        else:
            return jsonify({"error": "Failed to submit"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/get-csv-url", methods=["GET"])
def get_csv_url():
    """Returns a secure link to access the CSV file"""
    url = generate_presigned_url()
    if url:
        return jsonify({"csv_url": url}), 200
    else:
        return jsonify({"error": "Failed to generate CSV link"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
