import requests
import pandas as pd
import json

def printTrunc(*args, sep=' ', end='\n', file=None, flush=False):
    output = sep.join(str(arg) for arg in args) + end
    lines = output.splitlines()
    quoted_lines = [f'"{line}"' for line in lines]
    final_output = '\n'.join(quoted_lines)
    if len(final_output) > 5000:
        final_output = final_output[:5000] + '... [truncated]'
    print(final_output, end='', file=file, flush=flush)

url = "https://cz.fd-api.com/api/v5/graphql"

headers = {
    "apollographql-client-name": "web",
    "apollographql-client-version": "GROCERIES-MENU-MICROFRONTEND.25.11.0012",
    "content-type": "application/json;charset=UTF-8",
    "origin": "https://www.foodora.cz",
    "platform": "web",
    "referer": "https://www.foodora.cz/",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
    "x-global-entity-id": "DJ_CZ",
    "x-pd-language-id": "3",
    "x-requested-with": "XMLHttpRequest"
}

payload = {
    "query": "\n    \n    fragment ProductFields on Product {\n        attributes(keys: $attributes) {\n            key\n            value\n        }\n        activeCampaigns {\n            benefitQuantity\n            cartItemUsageLimit\n            description\n            discountType\n            discountValue\n            endTime\n            id\n            isAutoAddable\n            isBenefit\n            isTrigger\n            name\n            teaserFormat\n            totalTriggerThresholdFloat\n            triggerQuantity\n            type\n        }\n        badges\n        description\n        favourite\n        globalCatalogID\n        isAvailable\n        name\n        nmrAdID\n        originalPrice\n        packagingCharge\n        parentID\n        price\n        productBadges {\n            text\n            type\n        }\n        productID\n        stockAmount\n        stockPrediction\n        tags\n        type\n        urls\n        vendorID\n        weightableAttributes {\n            weightedOriginalPrice\n            weightedPrice\n            weightValue {\n                unit\n                value\n            }\n        }\n    }\n\n\n    query getProductsByCategoryList(\n        $attributes: [String!]\n        $categoryId: String!\n        $featureFlags: [FunWithFlag!]\n        $globalEntityId: String!\n        $isDarkstore: Boolean!\n        $locale: String!\n        $userCode: String\n        $vendorID: String!\n    ) {\n        categoryProductList(\n            input: {\n                categoryID: $categoryId\n                customerID: $userCode\n                funWithFlags: $featureFlags\n                globalEntityID: $globalEntityId\n                isDarkstore: $isDarkstore\n                locale: $locale\n                platform: \"web\"\n                vendorID: $vendorID\n            }\n        ) {\n            categoryProducts {\n                id\n                name\n                items {\n                    ...ProductFields\n                }\n            }\n        }\n    }\n",
    "variables": {
        "categoryId": "148702b5-883e-4eaa-a66d-6dee1ee2e7bc",
        "attributes": [
            "baseContentValue",
            "baseUnit",
            "freshnessGuaranteeInDays",
            "maximumSalesQuantity",
            "minPriceLastMonth",
            "pricePerBaseUnit",
            "sku",
            "nutri_grade",
            "sugar_level"
        ],
        "featureFlags": [
            {
                "key": "pd-qc-weight-stepper",
                "value": "Variation1"
            }
        ],
        "globalEntityId": "DJ_CZ",
        "isDarkstore": True,
        "locale": "cs_CZ",
        "vendorID": "l1hl"
    }
}

response = requests.post(url, headers=headers, json=payload)
data = response.json()

products = data['data']['categoryProductList']['categoryProducts'][0]['items']

product_list = []
for product in products:
    product_list.append({
        'name': product['name'],
        'price': product['price']
    })

df = pd.DataFrame(product_list)
printTrunc(df[['name', 'price']].to_string())
