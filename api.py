from flask import Flask, request, jsonify
from flask_cors import CORS
import csv
import boto3
import os
from dotenv import load_dotenv
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app)

# File and AWS S3 Configurations from environment variables
CSV_FILE = "enquiry_data.csv"
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
S3_FILE_NAME = "enquiry_data.html"
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
SENDER_EMAIL = "karimnagareurokids@gmail.com"
RECEIVER_EMAIL = "karimnagareurokids@gmail.com"  # You can change this if needed

# Initialize S3 Client
s3 = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY
)

# Ensure CSV file exists with headers
def initialize_csv():
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Parent Name", "Child Name", "Phone", "Email", "Class", "Occupation", "Address", "Referred By"])

initialize_csv()

def generate_html_from_csv():
    try:
        with open(CSV_FILE, "r") as file:
            reader = csv.reader(file)
            rows = list(reader)

        html_content = "<html><body><table border='1' style='width:100%; border-collapse: collapse;'>"
        for row in rows:
            html_content += "<tr>" + "".join(f"<td style='padding: 8px;'>{col}</td>" for col in row) + "</tr>"
        html_content += "</table></body></html>"

        html_file_path = os.path.join(os.getcwd(), "enquiry_data.html")
        with open(html_file_path, "w") as html_file:
            html_file.write(html_content)

        return html_file_path

    except Exception as e:
        print(f"Error generating HTML: {e}")
        return None

def upload_to_s3(html_file_path):
    try:
        if html_file_path:
            s3.upload_file(
                html_file_path,
                S3_BUCKET_NAME,
                S3_FILE_NAME,
                ExtraArgs={"ContentType": "text/html", "ACL": "public-read"}
            )
            print("HTML file uploaded successfully!")
            return True
        else:
            return False
    except Exception as e:
        print(f"Error uploading HTML to S3: {e}")
        return False

def send_email_notification(data):
    message = Mail(
        from_email='karimnagareurokids@gmail.com',
        to_emails='shailakar.bommakanti.22@gmail.com',
        subject='📩 New Enquiry Received',
        html_content=f"""
        <strong>New enquiry submitted!</strong><br><br>
        <b>Parent Name:</b> {data['parent_name']}<br>
        <b>Child Name:</b> {data['child_name']}<br>
        <b>Phone:</b> {data['phone']}<br>
        <b>Email:</b> {data['email']}<br>
        <b>Class:</b> {data['class']}<br>
        <b>Occupation:</b> {data['occupation']}<br>
        <b>Address:</b> {data['address']}<br>
        <b>Referred By:</b> {data['referred_by']}
        """
    )
    try:
        sg = SendGridAPIClient(ZPL6NB28KG5BTNA2X3DMU8WT)
        response = sg.send(message)
        print(f"Email sent! Status Code: {response.status_code}")
    except Exception as e:
        print(f"Error sending email: {e}")

@app.route("/")
def home():
    return "Server is running!"

@app.route("/submit", methods=["POST"])
def submit_form():
    try:
        data = request.json

        with open(CSV_FILE, mode="a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([
                data["parent_name"], data["child_name"], data["phone"], data["email"],
                data["class"], data["occupation"], data["address"], data["referred_by"]
            ])

        print("Data appended to CSV successfully!")

        html_file_path = generate_html_from_csv()
        upload_success = upload_to_s3(html_file_path)

        send_email_notification(data)

        if upload_success:
            return jsonify({"message": "Form submitted and email sent!"}), 200
        else:
            return jsonify({"error": "Data saved but failed to upload HTML"}), 500

    except Exception as e:
        print(f"Error in form submission: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/get-html-url", methods=["GET"])
def get_html_url():
    public_url = f"https://{S3_BUCKET_NAME}.s3.amazonaws.com/{S3_FILE_NAME}"
    return jsonify({"html_url": public_url}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
