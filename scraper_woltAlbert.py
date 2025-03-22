import requests
import pandas as pd

def printTrunc(*args, sep=' ', end='\n', file=None, flush=False):
    output = sep.join(str(arg) for arg in args) + end
    lines = output.splitlines()
    quoted_lines = [f'"{line}"' for line in lines]
    final_output = '\n'.join(quoted_lines)
    if len(final_output) > 5000:
        final_output = final_output[:5000] + '... [truncated]'
    print(final_output, end='', file=file, flush=flush)


url = "https://consumer-api.wolt.com/consumer-api/consumer-assortment/v1/venues/slug/albert-vinohradska/assortment/categories/slug/zelenina-257?language=cs"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
    "App-Language": "en",
    "Platform": "Web",
    "client-version": "1.14.79-PR16534",
    "clientversionnumber": "1.14.79-PR16534",
    "sec-ch-ua": '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"'
}

try:
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = response.json()

    potato_data = []
    for item in data['items']:
        if 'brambory' in item['name'].lower():
            potato_data.append({
                'name': item['name'],
                'price': item['price'] / 100, # Convert to CZK
                'unit_info': item['unit_info'],
                'unit_price': item['unit_price']['price'] / 100 if item['unit_price'] else None,
                'original_price': item['original_price'] / 100 if item['original_price'] else None
            })

    df = pd.DataFrame(potato_data)
    printTrunc(df.to_string())

except requests.exceptions.RequestException as e:
    printTrunc(f"Request error: {e}")
except (KeyError, TypeError) as e:
    printTrunc(f"JSON parsing error: {e}")
