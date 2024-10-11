import requests
from bs4 import BeautifulSoup

# Second task, getting the html page using a get request
url = "https://999.md/ro/87872146"
response = requests.get(url)
if response.status_code == 200:
    print("GET request was successful.")
else:
    print(f"Error occurred while processing the request = {response.status_code}")
html_response = response.text
soup = BeautifulSoup(html_response, 'html.parser')
f = open("html_response", 'w')

# Writing the html content in a file for storage
f.write(soup.prettify())
f.close()

# Fourth task, scrapping links from the URL
f = open("scrapped_data", "w")
seen_links = set()
product_names = set()
product_links = soup.find_all('a', {"class": "js-item-ad"})
link_dictionary = {f'{soup.title.string}': 'https://999.md/ro/87872146'}
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
    link_dictionary.update({name: link})
    # f.write(f"Product name: {name}, Product link: {link}\n")

# Third task, using a html parser to get the price of a product
for i, (name, link) in enumerate(link_dictionary.items()):
    f.write("Product listing #" + str(i) + '\n')
    f.write("Link = " + link + '\n')
    f.write("Product name = " + name + '\n')
    response = requests.get(link)
    if response.status_code == 200:
        print("GET request was successful.")
    else:
        print(f"Error occurred while processing the request = {response.status_code}")
    html_response = response.text
    soup = BeautifulSoup(html_response, 'html.parser')
    price_data = soup.find('ul', {"class": ["adPage__content__price-feature__prices"]})
    if price_data:
        prices = price_data.find_all('span', {"class": ["adPage__content__price-feature__prices__price__value"]})
        currencies = price_data.find_all('span', {"class": ["adPage__content__price-feature__prices__price__currency"]})
        numeric = '0123456789'
        standard_currency = ['€', '$', 'lei']
        for price, currency in zip(prices, currencies):
            price_value = price.get_text()
            currency_value = currency.get_text()
            # Error handling to ensure that the currency value is an int
            # and that the currency type is only euro, dollars & lei.
            for ch in price_value:
                if ch not in numeric:
                    price_value = price_value.replace(ch, '')
            try:
                price_value = int(price_value)
            except:
                price_value = "Error"
            if currency not in standard_currency:
                currency = "Error"
            f.write(f"Price: {price_value}, Currency: {currency_value}\n")
    else:
        f.write(f"Price: Negotiable|N/A\n")
    # Getting the location data
    location_data = soup.find('span', {"class": ["adPage__aside__address-feature__text"]})
    try:
        location_data = location_data.get_text(strip=True)
        if location_data:
            f.write(f"Location: {location_data}\n")
    except:
        f.write(f"Location: N/A\n")

f.close()

