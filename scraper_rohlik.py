import requests
import pandas as pd
import gzip
import io

def printTrunc(*args, sep=' ', end='\n', file=None, flush=False):
    output = sep.join(str(arg) for arg in args) + end
    lines = output.splitlines()
    quoted_lines = [f'"{line}"' for line in lines]
    final_output = '\n'.join(quoted_lines)
    if len(final_output) > 5000:
        final_output = final_output[:5000] + '... [truncated]'
    print(final_output, end='', file=file, flush=flush)

# Category ID for 'brambory' (potatoes)
category_id = "300102009"

# URL to fetch product IDs for the category
url_products = f"https://www.rohlik.cz/api/v1/categories/normal/{category_id}/products?page=0&size=14&sort=recommended&filter="

# Send request to get product IDs
response_products = requests.get(url_products)

if response_products.status_code == 200:
    data_products = response_products.json()
    product_ids = data_products["productIds"]

    # Construct the URL for prices API
    url_prices = "https://www.rohlik.cz/api/v1/products/prices?" + '&'.join([f"products={product_id}" for product_id in product_ids])

    # Send request to get prices
    response_prices = requests.get(url_prices)

    if response_prices.status_code == 200:
        data_prices = response_prices.json()

        # Extract relevant information
        prices = []
        for item in data_prices:
            prices.append({
                'product_id': item['productId'],
                'price': item['price']['amount'],
                'price_currency': item['price']['currency'],
                'unit_price': item['pricePerUnit']['amount'],
                'unit_currency': item['pricePerUnit']['currency']
            })

        df = pd.DataFrame(prices)
        printTrunc(df.to_string())

    else:
        printTrunc(f"Request failed with status code: {response_prices.status_code}")
else:
    printTrunc(f"Request failed with status code: {response_products.status_code}")