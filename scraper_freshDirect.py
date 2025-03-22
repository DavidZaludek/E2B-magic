import requests
import json

def printTrunc(*args, sep=' ', end='\n', file=None, flush=False):
    output = sep.join(str(arg) for arg in args) + end
    lines = output.splitlines()
    quoted_lines = [f'"{line}"' for line in lines]
    final_output = '\n'.join(quoted_lines)
    if len(final_output) > 5000:
        final_output = final_output[:5000] + '... [truncated]'
    print(final_output, end='', file=file, flush=flush)

url = "https://www.freshdirect.com/graphql"

headers = {
    "accept": "*/*",
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "en-US,en;q=0.9",
    "cache-control": "no-cache",
    "content-type": "application/json",
    "dnt": "1",
    "origin": "https://www.freshdirect.com",
    "pragma": "no-cache",
    "priority": "u=1, i",
    "referer": "https://www.freshdirect.com/fresh_produce/veg/sc/pot",
    "sec-ch-ua": '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
    "x-express-checkout-operation": "false",
    "x-express-filter": "undefined",
    "x-jabuticaba": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJGcmVzaERpcmVjdCIsIm5hbWUiOiJpT1MiLCJpYXQiOjE1MTYyMzkwMjJ9.g9YHW_5cP6pFn5dIQY9mZXTcVQzr0UPrVtDXvQRQook",
    "x-knock-token": "no-token",
    "x-service-type": "undefined"
}

data = json.dumps([{
    "operationName": "SubcategorySearch",
    "variables": {
        "subcategory": "pot",
        "pageRequest": {
            "page": 1,
            "pageSize": 12,
            "sort": None
        },
        "includeSubcategories": True,
        "filters": [{
            "facetId": "id",
            "facetValueIds": ["pot"]
        }]
    },
    "query": "query SubcategorySearch($subcategory: ID!, $pageRequest: PageRequest, $includeSubcategories: Boolean, $filters: [SearchFilter!]) {\n  subcategorySearch(\n    subcategory: $subcategory\n    pageRequest: $pageRequest\n    includeSubcategories: $includeSubcategories\n    filters: $filters\n  ) {\n    products {\n      productId\n      productName\n      formattedCurrentPrice\n      __typename\n    }\n    __typename\n  }\n}"
}])

response = requests.post(url, headers=headers, data=data)

if response.status_code == 200:
    json_data = response.json()

    if 'errors' in json_data[0]:
        printTrunc(f"Response: {json_data}")
    else:
        products = json_data[0]['data']['subcategorySearch']['products']
        for product in products:
            printTrunc(f"{product['productName']}: {product['formattedCurrentPrice']}")

else:
    printTrunc(f"Request failed with status code {response.status_code}")
