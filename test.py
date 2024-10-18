import base64
import requests

username = "204"
password = "408"
credentials = f"{username}:{password}"
token = base64.b64encode(credentials.encode()).decode()

headers = {
    "Authorization": f"Basic {token}"
}

print(token)

url = "http://localhost:8000/upload?message=test"
response = requests.post(url, headers=headers)

print(response.status_code)
print(response.text)