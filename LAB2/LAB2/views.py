from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import connections
from django.db.utils import OperationalError
import json
import xml.etree.ElementTree as ET
import os


@csrf_exempt
def get(request):
    if request.method == 'GET':
        # Establishing database connection
        db_conn = connections['default']
        try:
            c = db_conn.cursor()

            # Handle case for specific product ID
            product_id = request.GET.get('id')
            if product_id:
                try:
                    product_id = int(product_id)

                    # Checking if the product exists in the database
                    validation_query = """SELECT COUNT(*) FROM products WHERE product_listing = %s"""
                    c.execute(validation_query, (product_id,))
                    validated = c.fetchone()[0]

                    if validated > 0:
                        # Getting the product with matching product_id
                        query = """SELECT * FROM products WHERE product_listing = %s"""
                        c.execute(query, (product_id,))
                        result = c.fetchall()
                        
                        return HttpResponse(result, status=200)
                    else:
                        return HttpResponse("No matching product_id found in the database.", status=400)

                except ValueError:
                    return HttpResponse("Invalid Product ID parameter format.", status=400)
            else:
                return HttpResponse("Product ID parameter not provided.", status=400)

        except OperationalError as e:
            print("Database operation failed: ", e)
            return HttpResponse("Database error occurred.", status=500)
        finally:
            c.close()
    else:
        return HttpResponse("Invalid request method.", status=400)
    

@csrf_exempt
def get_all(request):
    if request.method == 'GET':
        # Establishing database connection
        db_conn = connections['default']
        try:
            c = db_conn.cursor()
            results_per_page = 5
            offset = 0

            # Pagination handling
            page = request.GET.get('page')
            if page:
                try:
                    page = int(page)
                    offset = results_per_page * page
                except ValueError:
                    return HttpResponse("Invalid datatype for page parameter", status=400)

            # Query to fetch all products with pagination
            query = """SELECT * FROM products LIMIT %s OFFSET %s"""
            c.execute(query, (results_per_page, offset))
            results = c.fetchall()

            # If no results, return a 404 response
            if not results:
                return HttpResponse("No products found.", status=400)

            return HttpResponse(results, status=200)

        except OperationalError as e:
            print("Database operation failed: ", e)
            return HttpResponse("Database error occurred.", status=500)
        finally:
            c.close()
    else:
        return HttpResponse("Invalid request method.", status=400)


@csrf_exempt
def post(request):
    if request.method == 'POST':
        # Reading the scrapped data from the previous lab
        try:
            f = open("LAB1/scrapped_data.txt", "r")
            scrapped_data = f.read().splitlines()
        except:
            return(HttpResponse("Scrapped data file not found."))
        
        # Preparing the data for db insertion
        pr_listings = []
        pr_links = []
        pr_titles = []
        pr_prices = []
        pr_currencies = []
        pr_locations = []
        pr_price_ranges = []

        for line in scrapped_data:
            if "Product listing #" in line:
                pr_listings.append(line.split("Product listing #")[1])
            elif "Link = " in line:
                pr_links.append(line.split("Link = ")[1])
            elif "Product name = " in line:
                pr_titles.append(line.split("Product name = ")[1])
            elif "Price: " in line:
                line = line.split("Price: ")[1]
                try:
                    pr_price, pr_currency = line.split(",")
                    pr_prices.append(pr_price)
                    pr_currencies.append(pr_currency.split("Currency: ")[1])
                except:
                    pr_prices.append("N/A")
                    pr_currencies.append("N/A")
            elif "Location: " in line:
                pr_locations.append(line.split("Location: ")[1])
            elif "Price-range: " in line:
                pr_price_ranges.append(line.split("Price-range: ")[1])
        
        # Inserting the scrapped data into the database
        db_conn = connections['default']
        try:
            c = db_conn.cursor()
        except OperationalError:
            print(OperationalError)
        else:
            for i in range(len(pr_listings)):
                try:
                    # Validating to see if the data was already inserted in the database
                    validation_query = """SELECT COUNT(*) FROM products WHERE product_listing = %s"""
                    c.execute(validation_query, (pr_listings[i],))
                    validated = c.fetchone()[0]
                    c.fetchall()

                    # If validated, we insert it, otherwise we skip it
                    if validated == 0:
                        query = """INSERT INTO products(product_listing, url, title, price, currency, location, price_range) 
                                VALUES (%s, %s, %s, %s, %s, %s, %s)"""


                        values = (pr_listings[i], pr_links[i], pr_titles[i], pr_prices[i], pr_currencies[i], pr_locations[i], pr_price_ranges[i])

                        c.execute(query, values)
                        db_conn.commit()
                    else:
                        print(f"Product listing {pr_listings[i]} already exists, skipping insertion.")
                        continue

                except OperationalError as e:
                    print("Database operation failed: ", e)
                finally:
                    # Closing the database connection
                    c.close()


        return(HttpResponse("Post operation successful", status=200))
    else:
        return HttpResponse("Invalid request method.", status=400)


@csrf_exempt
def delete(request):
    if request.method == 'DELETE':
        # Getting the query parameter
        product_id = request.GET.get('id')
        if product_id:
            try:
                # Validating input
                product_id = int(product_id)

                # Establishing database connection
                db_conn = connections['default']
                try:
                    c = db_conn.cursor()
                except OperationalError:
                    print(OperationalError)
                else:
                    try:
                        # Checking if the product exists in the database
                        validation_query = """SELECT COUNT(*) FROM products WHERE product_listing = %s"""
                        c.execute(validation_query, (product_id,))
                        validated = c.fetchone()[0]
                        c.fetchall()

                        if validated > 0:
                            # Deleting the product with matching product_id
                            query = """DELETE FROM products WHERE product_listing = %s"""
                            c.execute(query, (product_id,))
                            db_conn.commit()
                            return HttpResponse(f"Product with product_id={product_id} deleted from database.", status=200)
                        else:
                            return HttpResponse("No matching product_id found in the database.", status=404)
                    
                    except OperationalError as e:
                        print("Database operation failed: ", e)
                    finally:
                        c.close()

            except ValueError:
                return HttpResponse("Invalid Product ID parameter format.", status=400)
        else:
            return HttpResponse("Product ID parameter not provided.", status=400)

    else:
        return HttpResponse("Invalid request method.")

@csrf_exempt
def put(request):
    if request.method == 'PUT':
        # Getting the query parameter
        product_id = request.GET.get('id')
        if product_id:
            try:
                # Validating input
                product_id = int(product_id)

                # Establishing database connection
                db_conn = connections['default']
                try:
                    c = db_conn.cursor()
                except OperationalError:
                    print(OperationalError)
                else:
                    try:
                        # Checking if the product exists in the database
                        validation_query = """SELECT COUNT(*) FROM products WHERE product_listing = %s"""
                        c.execute(validation_query, (product_id,))
                        validated = c.fetchone()[0]
                        c.fetchall()
                        
                        # If the product doesn't exist, we create it, otherwise, we update it.
                        if validated > 0:
                            # Getting the product with matching product_id
                            query = """UPDATE products SET """
                            updates = []
                            values = []

                            if 'url' in request.GET:
                                updates.append("url = %s")
                                values.append(request.GET['url'])

                            if 'title' in request.GET:
                                updates.append("title = %s")
                                values.append(request.GET['title'])

                            if 'price' in request.GET:
                                updates.append("price = %s")
                                values.append(request.GET['price'])
                            
                            if 'currency' in request.GET:
                                updates.append("currency = %s")
                                values.append(request.GET['currency'])
                            
                            if 'location' in request.GET:
                                updates.append("location = %s")
                                values.append(request.GET['location'])

                            if 'price_range' in request.GET:
                                updates.append("price_range = %s")
                                values.append(request.GET['price_range'])

                            if not updates:
                                return HttpResponse("No updates were provided in query parameters.", status=400)
                            
                            query += ", ".join(updates) + " WHERE product_listing = %s"
                            print(query)
                            values.append(product_id)


                            c.execute(query, values)
                            db_conn.commit()
                            
                            return HttpResponse(f"Product with product_id={product_id} successfully updated in the database.", status=200)
                        else:
                            query = """INSERT INTO products(product_listing, url, title, price, currency, location, price_range) 
                                    VALUES (%s, %s, %s, %s, %s, %s, %s)"""
                            
                            values = []
                            values.append(product_id)

                            if 'url' in request.GET:
                                values.append(request.GET['url'])

                            if 'title' in request.GET:
                                values.append(request.GET['title'])

                            if 'price' in request.GET:
                                values.append(request.GET['price'])
                            
                            if 'currency' in request.GET:
                                values.append(request.GET['currency'])
                            
                            if 'location' in request.GET:
                                values.append(request.GET['location'])

                            if 'price_range' in request.GET:
                                values.append(request.GET['price_range'])

                            if len(values) != 7:
                                return HttpResponse("Cannot add new database entry; make sure all required values are provided in query parameters.", status=400)
                            
                            c.execute(query, values)
                            db_conn.commit()

                            return HttpResponse(f"Product with product_listing={product_id} successfully added to the database.", status=200)
                    
                    except OperationalError as e:
                        print("Database operation failed: ", e)
                    finally:
                        c.close()

            except ValueError:
                return HttpResponse("Invalid Product ID parameter format.", status=400)
        else:
            return HttpResponse("Product ID parameter not provided.", status=400)
    else:
        return HttpResponse("Invalid request method.", status=400)


def read_json_files(file_content):
    try:
        file_data = json.loads(file_content)
        for item in file_data:
            product_listing = item.get('product_listing')
            link = item.get('link')
            product_name = item.get('product_name')
            price = item.get('price')
            currency = item.get('currency')
            location = item.get('location')
            price_range = item.get('price_range')

            # Inserting the tuple into the database
            insert_into_database((product_listing, link, product_name, price, currency, location, price_range))

    except json.JSONDecodeError:
            return HttpResponse("Invalid file format detected", status=400)


def read_xml_files(file_content):
    try:
        root = ET.fromstring(file_content)

        for product in root.findall('product'):
            product_listing = product.find('product_listing').text
            link = product.find('link').text
            product_name = product.find('product_name').text
            price = product.find('price').text
            currency = product.find('currency').text
            price_range = product.find('price_range').text
            location = product.find('location').text

            # Inserting the tuple into the database
            insert_into_database((product_listing, link, product_name, price, currency, location, price_range))
        
    except ET.ParseError:
        return HttpResponse("Error while parsing xml file.", status=400)


def insert_into_database(values):
    db_conn = connections['default']
    try:
        c = db_conn.cursor()
    except OperationalError:
        print(OperationalError)
    else:
        try:
            # Validating to see if the data was already inserted in the database
            validation_query = """SELECT COUNT(*) FROM products WHERE product_listing = %s"""
            c.execute(validation_query, (values[0],))
            validated = c.fetchone()[0]
            c.fetchall()

            # If validated, we insert it, otherwise we skip it
            if validated == 0:
                query = """INSERT INTO products(product_listing, url, title, price, currency, location, price_range) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s)"""

                c.execute(query, values)
                db_conn.commit()
            else:
                print(f"Product listing {values[0]} already exists, skipping insertion.")

        except OperationalError as e:
            print("Database operation failed: ", e)
        finally:
            # Closing the database connection
            c.close()


@csrf_exempt
def upload(request):
    if request.method == "POST":
        # Checking if files were provided along with the request
        if 'file' not in request.FILES:
            return HttpResponse("No files were uploaded.", status=400)
        # Iterating each file and checking their type
        for file in request.FILES.getlist('file'):
            try:
                file_content = file.read().decode('utf-8')
                file_name = file.name
                # Executing the relevant function based on file extension
                if os.path.splitext(file_name)[1] == '.json':
                    read_json_files(file_content)
                elif os.path.splitext(file_name)[1] == '.xml':
                    read_xml_files(file_content)
                else:
                    return HttpResponse("File format not accepted.", status=400)
            except json.JSONDecodeError:
                return HttpResponse("Invalid file format detected", status=400)
            
            return HttpResponse("File successfully read and uploaded to the database", status=200)

    return HttpResponse("Invalid request method used.", status=400)

