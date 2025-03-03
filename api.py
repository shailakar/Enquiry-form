import requests
import base64

# GitHub repo details
repo = "shailakar/Enquiry-form"
file_path = "data.csv"
github_token = "your_github_token"

# Read updated file content
with open("updated_data.csv", "rb") as f:
    content = f.read()
    content_b64 = base64.b64encode(content).decode("utf-8")

# GitHub API URL
url = f"https://api.github.com/repos/{repo}/contents/{file_path}"

# Fetch the current file SHA (needed for update)
headers = {"Authorization": f"token {github_token}"}
response = requests.get(url, headers=headers)
sha = response.json().get("sha", "")

# Prepare API request to update file
data = {
    "message": "Update sheet data",
    "content": content_b64,
    "sha": sha
}

# Update file in GitHub
response = requests.put(url, json=data, headers=headers)
print(response.json())
