import requests
import gzip
import json

url = "https://www.rohlik.cz/api/v1/categories/normal/300102009/products?page=0&size=14&sort=recommended&filter="

headers = {
    'accept': '*/*',
    'accept-encoding': 'gzip, deflate, br, zstd',
    'accept-language': 'en-US,en;q=0.9',
    'cache-control': 'no-cache',
    'dnt': '1',
    'pragma': 'no-cache',
    'priority': 'u=1, i',
    'referer': 'https://www.rohlik.cz/c300102009-brambory',
    'sec-ch-ua': '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
    'x-origin': 'WEB'
}

try:
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
    # Rohlik uses gzip compression, so decode accordingly
    json_data = response.json()

    product_ids = json_data['productIds']
    
    product_prices_url = "https://www.rohlik.cz/api/v1/products/prices?"
    product_prices_url += '&'.join([f'products={product_id}' for product_id in product_ids])
    
    product_prices_response = requests.get(product_prices_url, headers=headers)
    product_prices_response.raise_for_status()
    product_prices = product_prices_response.json()
    
    for product_price in product_prices:
        print(f"Product ID: {product_price['productId']}, Price: {product_price['price']['amount']} {product_price['price']['currency']}")

except requests.exceptions.RequestException as e:
    print(f"Request error: {e}")
except (KeyError, TypeError, ValueError) as e:
    print(f"Error processing the response: {e}")
