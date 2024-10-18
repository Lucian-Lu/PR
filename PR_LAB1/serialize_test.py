import ast

def serialize_xml(data):
    # Function to serialize dictionaries
    def dict_to_xml(data):
        xml_str = '<product_data>\n'
        xml_str += '\t<filtered_products>\n'

        # Using ast to convert the filtered_products string to a dictionary
        filtered_products = ast.literal_eval(data['filtered_products'])

        for product in filtered_products:
            xml_str += "\t\t<product>\n"

            xml_str += f"\t\t\t<product_listing>{product['product_listing']}</product_listing>\n"
            xml_str += f"\t\t\t<url>{product['url']}</url>\n"
            xml_str += f"\t\t\t<title>{product['title']}</title>\n"
            xml_str += f"\t\t\t<price>{product['price']}</price>\n"
            xml_str += f"\t\t\t<currency>{product['currency']}</currency>\n"
            xml_str += f"\t\t\t<location>{product['location']}</location>\n"
            xml_str += f"\t\t\t<price-range>{product['price-range']}</price-range>\n"
        xml_str += '\t</filtered_products>\n'
        xml_str += f"\t<filtered_products_sum>{data['filtered_products_sum']}</filtered_products_sum>\n"
        xml_str += f"\t<timestamp>{data['timestamp']}</timestamp>\n"
        xml_str += '</product_data>'
        return xml_str
    
    if isinstance(data, dict):
        return dict_to_xml(data)
    else:
        raise Exception("Error: Unsupported data type when serializing to xml.")

filtered_products_results = {
  "filtered_products": "[{'product_listing': 4, 'url': 'https://999.md/ro/87872146', 'title': 'Jante Arceo Marseille R19 5x120 Glossy Black', 'price': 874, 'currency': '€', 'location': 'N/A', 'price-range': 3}, {'product_listing': 7, 'url': 'https://999.md/ro/87872146', 'title': '225/55 R16 Tracmax. (2024). Hовая! Летo! Доставка!', 'price': 1040, 'currency': '€', 'location': 'N/A', 'price-range': 3}]",
  "filtered_products_sum": "1914",
  "timestamp": "2024-10-18T09:51:30.788006"
}
json_obj = serialize_xml(filtered_products_results)
print(json_obj)