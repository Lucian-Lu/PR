# import requests
from bs4 import BeautifulSoup
import functools
from datetime import datetime, timezone
import socket, ssl

def get_eur_price(price_currency_pair):
    numeric = '0123456789'

    price, currency = price_currency_pair
    price_value = price.get_text()
    currency_value = currency.get_text()

    # Error handling to ensure that the currency value is an int
    # and that the currency type is only euro.
    price_value = ''.join([ch for ch in price_value if ch in numeric])
    currency_value = ''.join([ch for ch in currency_value if ch in '€'])

    try:
        price_value = int(price_value)
    except ValueError:
        price_value = "Error"
    
    if currency_value == '€':
        return price_value
    

def add_product_price_range(products):
    for product in products:
        # Adding price ranges for the products
        if isinstance(product['price'], int):
            if product['price'] < 100:
                product['price-range'] = 1
            elif product['price'] < 500:
                product['price-range'] = 2
            elif product['price'] < 2500:
                product['price-range'] = 3
            elif product['price'] < 10000:
                product['price-range'] = 4
            else:
                product['price-range'] = 5
        else:
            product['price-range'] = 0

    return products

def is_in_price_range(product, price_range_id):
    return product.get('price-range') == price_range_id


def serialize_json(data):
    # Function to serialize dictionaries
    def dict_to_json(dictionary, in_list=False):
        json_str = '{\n'
        for i, (key, value) in enumerate(dictionary.items()):
            json_str += f'  "{key}": "{value}"'
            if i < len(dictionary) - 1:
                json_str += ',\n'
        if not in_list:
            json_str += '\n}'
        else:
            json_str += '\n }'
        return json_str

    # Function to serialize dictionary lists
    def list_to_json(dictonary_list):
        json_str = '[\n'
        for i, item in enumerate(dictonary_list):
            json_str += ' ' + dict_to_json(item, True)
            if i < len(dictonary_list) - 1:
                json_str += ',\n'
            else:
                json_str += ' '
        json_str += '\n]'
        return json_str

    if isinstance(data, dict):
        return dict_to_json(data)
    elif isinstance(data, list):
        return list_to_json(data)
    else:
        raise Exception("Error: Unsupported data type when serializing to json.")
    

def serialize_xml(data):
    # Function to serialize dictionaries
    def dict_to_xml(data):
        xml_str = '<product_data>\n'
        xml_str += '\t<filtered_products>\n'

        filtered_products = data['filtered_products']
        for product in filtered_products:
            xml_str += "\t\t<product>\n"

            xml_str += f"\t\t\t<product_listing>{product['product_listing']}</product_listing>\n"
            xml_str += f"\t\t\t<url>{product['url']}</url>\n"
            xml_str += f"\t\t\t<title>{product['title']}</title>\n"
            xml_str += f"\t\t\t<price>{product['price']}</price>\n"
            xml_str += f"\t\t\t<currency>{product['currency']}</currency>\n"
            xml_str += f"\t\t\t<location>{product['location']}</location>\n"
            xml_str += f"\t\t\t<price-range>{product['price-range']}</price-range>\n"
            
            xml_str += '\t\t</product>'

        xml_str += '\t</filtered_products>\n'
        xml_str += f"\t<filtered_products_sum>{data['filtered_products_sum']}</filtered_products_sum>\n"
        xml_str += f"\t<timestamp>{data['timestamp']}</timestamp>\n"
        xml_str += '</product>'

        return xml_str
    
    if isinstance(data, dict):
        return dict_to_xml(data)
    else:
        raise Exception("Error: Unsupported data type when serializing to xml.")


# Seventh task, using sockets instead of requests library
def send_https_request(host, path):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)   
    # Wrapping the socket for HTTPS connection
    s_socket = ssl.wrap_socket(sock)
    
    try:
        # Connecting to the server on the https port
        s_socket.connect((host, 443))
        request = f"GET {path} HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n"
        s_socket.sendall(request.encode())
        
        # Receive the response in chunks
        response = b""
        while True:
            chunk = s_socket.recv(4096)
            if not chunk:
                break
            response += chunk
        
        response_str = response.decode('utf-8')
        # Split the response into headers and body
        header, _, body = response_str.partition("\r\n\r\n")
        
        return body
    finally:
        s_socket.close()

# Ninth task - custom serialization/deserialization
# Custom serialization - available data types:
# L = list; D = dictionary; K = key; V = value; I = integer; F = float; N = none; O = other
def custom_serialize(data):
    # Serializing dictionaries
    if isinstance(data, dict):
        serialized_dict = "D:\n"
        for key, value in data.items():
            serialized_dict += f"\t\tK:{key}|V:{custom_serialize(value)}\n"
        serialized_dict += "\t/D"
        return serialized_dict
    
    # Serializing lists
    elif isinstance(data, list):
        serialized_list = "L:\n"
        for item in data:
            serialized_list += f"\t{custom_serialize(item)}\n"
        serialized_list += "/L"
        return serialized_list
    
    # Serializing basic data types
    elif isinstance(data, str):
        return f"S({data})"
    elif isinstance(data, int):
        return f"I({data})"
    elif isinstance(data, float):
        return f"F({data})"
    elif data is None:
        return "N"
    else:
        return f"O({str(data)})"


def custom_deserialize(serialized):
    stack = []
    current_dict = None
    current_list = None
    # Splitting each line
    lines = serialized.strip().splitlines()

    for line in lines:
        # Remove whitespaces
        line = line.strip()

        if line.startswith("L:"):
            # Start of a new list
            current_list = []
            stack.append(current_list)
        elif line.startswith("/L"):
            # End of the current list
            if len(stack) > 1:
                top_list = stack.pop()
                stack[-1].append(top_list)
            current_list = None
        elif line.startswith("D:"):
            # Start of a new dictionary
            current_dict = {}
            stack.append(current_dict)
        elif line.startswith("/D"):
            # End of the current dictionary
            if len(stack) > 1:
                top_dict = stack.pop()
                stack[-1].append(top_dict)
            current_dict = None
        elif line.startswith("K:"):
            # Splitting & removing prefixes
            key_value = line.split("|")
            key = key_value[0][2:]
            value = key_value[1][2:]
            if current_dict is not None:
                # Deserialize the value based on its type prefix
                value_type = value[0]
                if value_type == "S":
                    deserialized_value = value[2:-1]
                elif value_type == "I":
                    deserialized_value = int(value[2:-1])
                elif value_type == "F":
                    deserialized_value = float(value[2:-1])
                elif value_type == "N":
                    deserialized_value = None
                elif value_type == "O":
                    deserialized_value = value[2:-1]
                else:
                    raise ValueError(f"Error: Invalid type prefix: {value_type}")

                current_dict[key] = deserialized_value
        else:
            # Handle standalone values (basic types)
            if line.startswith("S("):
                value = line[2:-1]
                if current_list is not None:
                    current_list.append(value)
                else:
                    return value
            elif line.startswith("I("):
                value = int(line[2:-1])
                if current_list is not None:
                    current_list.append(value)
                else:
                    return value
            elif line.startswith("F("):
                value = float(line[2:-1])
                if current_list is not None:
                    current_list.append(value)
                else:
                    return value
            elif line == "N":
                if current_list is not None:
                    current_list.append(None)
                else:
                    return None
            elif line.startswith("O("):
                value = line[2:-1]
                if current_list is not None:
                    current_list.append(value)
                else:
                    return value

    # Return the root of the structure
    return stack[0] if stack else None


# Second task, getting the html page using a get request
# url = "https://999.md/ro/87872146"
# response = requests.get(url)
# if response.status_code == 200:
#     print("GET request was successful.")
# else:
#     print(f"Error occurred while processing the request = {response.status_code}")
# html_response = response.text
host = "999.md"
path = "/ro/87872146"
html_response = send_https_request(host, path)

soup = BeautifulSoup(html_response, 'html.parser')
f = open("html_response", 'w')

# Writing the html content in a file for storage
f.write(soup.prettify())
f.close()

# Fourth task, scrapping links from the URL
f = open("scrapped_data.txt", "w")

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

# Third task, using a html parser to get the price of a product
temp_dict_list = []
for i, (name, link) in enumerate(link_dictionary.items()):

    temp_dict = {}
    temp_dict["product_listing"] = i
    temp_dict["url"] = link
    temp_dict["title"] = name

    f.write("Product listing #" + str(i) + '\n')
    f.write("Link = " + link + '\n')
    f.write("Product name = " + name + '\n')

    # response = requests.get(link)
    # if response.status_code == 200:
    #     print("GET request was successful.")
    # else:
    #     print(f"Error occurred while processing the request = {response.status_code}")
    
    # html_response = response.text

    host, path = link.split("://")[-1].split("/", 1)
    path = "/" + path if path else ""
    html_response = send_https_request(host, path)

    soup = BeautifulSoup(html_response, 'html.parser')
    price_data = soup.find('ul', {"class": ["adPage__content__price-feature__prices"]})

    if price_data:
        prices = price_data.find_all('span', {"class": ["adPage__content__price-feature__prices__price__value"]})
        currencies = price_data.find_all('span', {"class": ["adPage__content__price-feature__prices__price__currency"]})

        price_currency_pair = zip(prices, currencies)
        eur_prices = map(get_eur_price, price_currency_pair)

        flag = 0
        for eur_price in eur_prices:
            if isinstance(eur_price, int):
                flag = 1
                f.write(f"Price: {eur_price}, Currency: €\n")
                temp_dict["price"] = eur_price
                temp_dict["currency"] = '€'
        if flag == 0:
            f.write(f"Price: Negotiable|N/A\n")
            temp_dict["price"] = "Negotiable|N/A"
            f.write(f"Currency: N/A\n")
            temp_dict["currency"] = "N/A"

    else:
        f.write(f"Price: Negotiable|N/A\n")
        temp_dict["price"] = "Negotiable|N/A"
        f.write(f"Currency: N/A\n")
        temp_dict["currency"] = "N/A"

    # Getting the location data
    location_data = soup.find('span', {"class": ["adPage__aside__address-feature__text"]})
    try:
        location_data = location_data.get_text(strip=True)
        if location_data:
            f.write(f"Location: {location_data}\n")
            temp_dict["location"] = location_data
    except:
        f.write(f"Location: N/A\n")
        temp_dict["location"] = "N/A"
    temp_dict_list.append(temp_dict)

# Sixth task, use of map, filter & reduce functions

temp_dict_list = add_product_price_range(temp_dict_list)
price_range_id = input("Select the price-range products you want to view (0-5): ")
try:
    price_range_id = int(price_range_id)
    if price_range_id >= 0 and price_range_id <= 5:
        filtered_products = list(filter(lambda product: is_in_price_range(product, price_range_id), temp_dict_list))
        # print(filtered_products)
        filtered_products_sum = functools.reduce(
            lambda current, product: current + product['price'] if isinstance(product['price'], (int)) else current,
            filtered_products,
            0
        )

        filtered_products_results = {
            "filtered_products": filtered_products,
            "filtered_products_sum": filtered_products_sum,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        # print('Sum of the products in price range[' + str(price_range_id) + '] = ' + str(filtered_products_sum))

except ValueError:
    print("Invalid data format.")

# Eighth task, serializing to json and xml
f.close()

f = open("serialize_json", 'w')
f.write(serialize_json(filtered_products_results))
f.close()

f = open("serialize_xml", 'w')
f.write(serialize_xml(filtered_products_results))
f.close()

# Ninth task, custom serialization/deserialization
f = open("custom_serialize", 'w')
custom_serialized = custom_serialize (temp_dict_list)
f.write(custom_serialized)

custom_deserialized = custom_deserialize(custom_serialized)

# print(custom_serialized)
# print(custom_deserialized)

# print(serialize_json(temp_dict_list))

