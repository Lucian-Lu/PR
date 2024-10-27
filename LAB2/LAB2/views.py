from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import connections
from django.db.utils import OperationalError


@csrf_exempt
def get(request):
    if request.method == 'GET':
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
                            # Getting the product with matching product_id
                            query = """SELECT * FROM products WHERE product_listing = %s"""
                            c.execute(query, (product_id,))
                            result = c.fetchall()
                            
                            return HttpResponse(result, status=200)
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


        return(HttpResponse("ok"))
    else:
        return HttpResponse("Invalid request method.")


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
        return HttpResponse("Invalid request method.")