import requests
from bs4 import BeautifulSoup

# Second task, getting the html page using a get request
url = "https://999.md/ro/87872146"
response = requests.get(url)
html_response = response.text
soup = BeautifulSoup(html_response, 'html.parser')
f = open("html_response", 'w')
# Writing the html content in a file for storage
f.write(soup.prettify())
f.close()
if response.status_code == 200:
    print("GET request was successful.")
else:
    print(f"Error occurred while processing the request = {response.status_code}")

# Third task, using a html parser to get the price and name of a product
f = open("scrapped_data", "w")
f.write(soup.title.string + '\n')
price_data = soup.find('ul', {"class": ["adPage__content__price-feature__prices"]})
if price_data:
    prices = price_data.find_all('span', {"class": ["adPage__content__price-feature__prices__price__value"]})
    currencies = price_data.find_all('span', {"class": ["adPage__content__price-feature__prices__price__currency"]})
    for price, currency in zip(prices, currencies):
        price_value = price.get_text()
        currency_value = currency.get_text()
        f.write(f"Price: {price_value}, Currency: {currency_value}\n")
else:
    print("No price data found.")
f.close()