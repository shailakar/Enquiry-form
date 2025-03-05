
from flask import Flask, request, jsonify
from flask_cors import CORS
import csv
import boto3
import os

app = Flask(__name__)
CORS(app, origins=["https://www.eurokidskarimnagar.me"])

# File and AWS S3 Configurations
CSV_FILE = "enquiry_data.csv"
AWS_ACCESS_KEY = "AKIA5CSKK24EK2NCIJPK"  # Replace with your AWS Access Key
AWS_SECRET_KEY = "tSwivYku7hn62HUoIq7Ci9akczBc97bmjZaMgR7Q"  # Replace with your AWS Secret Key
S3_BUCKET_NAME = "enquiryform01"  # Your S3 bucket name
S3_FILE_NAME = "enquiry_data.html"  # File name in S3 as HTML

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

def generate_html_from_csv():
    """Reads the CSV and converts it into an HTML table"""
    try:
        with open(CSV_FILE, "r") as file:
            reader = csv.reader(file)
            rows = list(reader)
        
        html_content = "<html><body><table border='1' style='width:100%; border-collapse: collapse;'>"
        for row in rows:
            html_content += "<tr>" + "".join(f"<td style='padding: 8px;'>{col}</td>" for col in row) + "</tr>"
        html_content += "</table></body></html>"

        # Save as an HTML file
        with open("enquiry_data.html", "w") as html_file:
            html_file.write(html_content)
        
        return "enquiry_data.html"

    except Exception as e:
        print(f"Error generating HTML: {e}")
        return None

def upload_to_s3():
    """Uploads the updated HTML file to S3 and makes it public"""
    try:
        html_file = generate_html_from_csv()
        if html_file:
            s3.upload_file(
                html_file,  # Local HTML file
                S3_BUCKET_NAME,  # S3 bucket name
                S3_FILE_NAME,  # S3 file name
                ExtraArgs={"ContentType": "text/html", "ACL": "public-read"}  # Set correct content type & make it public
            )
            print("HTML file uploaded successfully!")
            return True
        else:
            return False
    except Exception as e:
        print(f"Error uploading HTML to S3: {e}")
        return False

@app.route("/")
def home():
    return "Server is running!"

@app.route("/submit", methods=["POST"])
def submit_form():
    """Save form data to CSV and upload it as an HTML table to S3"""
    try:
        data = request.json

        # Append data to CSV file (instead of overwriting)
        with open(CSV_FILE, mode="a", newline="") as file:  # "a" for append mode
            writer = csv.writer(file)
            writer.writerow([
                data["parent_name"],
                data["child_name"],
                data["phone"],
                data["email"],
                data["dob"],
                data["class"],
                data["occupation"],
                data["address"],
                #data["Referred by"]
            ])
        
        print("Data appended to CSV successfully!")

        # Upload CSV as HTML to S3 (publicly viewable)
        success = upload_to_s3()

        if success:
            return jsonify({"message": "Form submitted successfully!"}), 200
        else:
            return jsonify({"error": "Failed to upload HTML to S3"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/get-html-url", methods=["GET"])
def get_html_url():
    """Returns a public URL to access the HTML file directly"""
    public_url = f"https://{S3_BUCKET_NAME}.s3.amazonaws.com/{S3_FILE_NAME}"
    return jsonify({"html_url": public_url}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
