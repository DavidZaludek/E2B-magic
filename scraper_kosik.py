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

url = "https://www.kosik.cz/api/front/page/products/flexible"
params = {
    "slug": "c1015-brambory-a-bataty",
    "limit": 30,
    "search_term": "",
    "page_display": "full",
}

try:
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()

    products = data['products']['items']
    df = pd.DataFrame(products)
    df_trimmed = df[['name', 'price', 'unit', 'pricePerUnit']]

    df_trimmed['unitForPricePerUnit'] = df['pricePerUnit'].apply(lambda x: x['unit'] if isinstance(x, dict) else '')

    printTrunc(df_trimmed.to_string())

except requests.exceptions.RequestException as e:
    printTrunc(f"Request Error: {e}")
except Exception as e:
    printTrunc(f"Error: {e}")
