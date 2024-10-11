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
# Getting the location data
location_data = soup.find('span', {"class": ["adPage__aside__address-feature__text"]})
location_data = location_data.get_text(strip=True)
f.write(f"Location: {location_data}\n")

# Fourth task, scrapping links from the URL
seen_links = set()
product_names = set()
product_links = soup.find_all('a', {"class": "js-item-ad"})
for product_link in product_links:
    product_name = product_link.get_text(strip=True)
    link = product_link.get('href')

    # Creating the full link from relative links
    if link.startswith('/'):
        link = "https://999.md" + link

    # Appending to the set if there's no duplicates
    if link not in seen_links:
        seen_links.add(link)
    if product_name not in product_names and product_name != '':
        product_names.add(product_name)

# Writing the data to the file
for name, link in zip(product_names, seen_links):
    f.write(f"Product name: {name}, Product link: {link}\n")

f.close()

