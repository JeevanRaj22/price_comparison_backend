from difflib import SequenceMatcher
import json

def normalize_name(name):
    return name.lower().replace(" ", "").replace("-", "").replace("(", "").replace(")", "").replace("″", "").replace("”", "").replace("smartphone","").replace("ai","")

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

def get_first_five_words(name):
    return " ".join(name.split()[:5])

# def find_matching_products_first_five_words(amazon_products, flipkart_products, threshold=0.8):
#     matched_products = []

#     for amazon_product in amazon_products:
#         for flipkart_product in flipkart_products:
#             amazon_name = normalize_name(amazon_product['name'])
#             flipkart_name = normalize_name(flipkart_product['name'])
#             print(amazon_name+" "+flipkart_name)
#             if (similar(amazon_name, flipkart_name) > threshold and
#                 amazon_product['color'].lower() == flipkart_product['color'].lower() and
#                 amazon_product['ram'] == flipkart_product['ram'] and
#                 amazon_product['rom'] == flipkart_product['rom']):
#                 matched_products.append({
#                     'Amazon Name': amazon_product['name'],
#                     'Flipkart Name': flipkart_product['name'],
#                     'image': amazon_product['img_url'],
#                     'amazon_url': amazon_product['url'],
#                     'flipkart_url' : flipkart_product['url'],
#                     'amazon_price' : amazon_product['price'],
#                     'flipkart_price' : flipkart_product['price'],
#                     'ram': amazon_product['ram'],
#                     'rom' : amazon_product['rom'],
#                     'color' : amazon_product['color']
#                 })
#     return matched_products
def find_matching_products_first_five_words(amazon_products, flipkart_products, threshold=0.75):
    matched_products = []

    # Make a copy of the product lists to avoid modifying the original lists during iteration
    amazon_products_copy = amazon_products[:]
    flipkart_products_copy = flipkart_products[:]

    for amazon_product in amazon_products:
        for flipkart_product in flipkart_products:
            amazon_name = normalize_name(amazon_product['name'])
            flipkart_name = normalize_name(flipkart_product['name'])
            # print(amazon_name + " " + flipkart_name)

            if (similar(amazon_name, flipkart_name) > threshold and
                amazon_product['color'].lower() == flipkart_product['color'].lower() and
                amazon_product['ram'] == flipkart_product['ram'] and
                amazon_product['rom'] == flipkart_product['rom']):
                
                # Add matched product to the list
                matched_products.append({
                    'Amazon Name': amazon_product['name'],
                    'Flipkart Name': flipkart_product['name'],
                    'image': amazon_product['img_url'],
                    'amazon_url': amazon_product['url'],
                    'flipkart_url': flipkart_product['url'],
                    'amazon_price': amazon_product['price'],
                    'flipkart_price': flipkart_product['price'],
                    'ram': amazon_product['ram'],
                    'rom': amazon_product['rom'],
                    'color': amazon_product['color']
                })

                # Remove the matched products from both lists
                if amazon_product in amazon_products_copy:
                    amazon_products_copy.remove(amazon_product)
                if flipkart_product in flipkart_products_copy:
                    flipkart_products_copy.remove(flipkart_product)

                # Break out of the inner loop as the Flipkart product is already matched
                break

    return matched_products, amazon_products_copy, flipkart_products_copy
