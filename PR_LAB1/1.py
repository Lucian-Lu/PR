import requests

url = "https://999.md/ro/87872146"
response = requests.get(url)
html_response = response.text
f = open("html_response", 'w')
f.write(html_response)
print("Get request response code = " + str(response))
