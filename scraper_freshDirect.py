import requests
import json
import pandas as pd

def printTrunc(*args, sep=' ', end='\n', file=None, flush=False):
    output = sep.join(str(arg) for arg in args) + end
    lines = output.splitlines()
    quoted_lines = [f'"{line}"' for line in lines]
    final_output = '\n'.join(quoted_lines)
    if len(final_output) > 5000:
        final_output = final_output[:5000] + '... [truncated]'
    print(final_output, end='', file=file, flush=flush)

try:
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
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
        "x-express-checkout-operation": "false",
        "x-express-filter": "undefined",
        "x-knock-token": "no-token",
        "x-service-type": "undefined"
    }

    payload = json.dumps([{
        "operationName": "SubcategorySearch",
        "variables": {
            "subcategory": "pot",
            "pageRequest": {
                "page": 1,
                "pageSize": 50,
                "sort": None
            },
            "includeSubcategories": True,
            "filters": [{
                "facetId": "id",
                "facetValueIds": ["pot"]
            }]
        },
        "query": "query SubcategorySearch($subcategory: ID!, $pageRequest: PageRequest, $includeSubcategories: Boolean, $filters: [SearchFilter!]) {\n  subcategorySearch(\n    subcategory: $subcategory\n    pageRequest: $pageRequest\n    includeSubcategories: $includeSubcategories\n    filters: $filters\n  ) {\n    products {\n      ...productTileFragment\n      __typename\n    }\n    recommendationCarousel {\n      products {\n        ...productTileFragment\n        __typename\n      }\n      __typename\n    }\n    breadcrumbs {\n      ...breadcrumbFragment\n      __typename\n    }\n    categories {\n      ...categoryFragment\n      categories {\n        ...categoryFragment\n        __typename\n      }\n      __typename\n    }\n    pillsFilter {\n      ...facetFragment\n      __typename\n    }\n    facets {\n      ...facetFragment\n      __typename\n    }\n    sortOptions {\n      ...SortOptionFragment\n      __typename\n    }\n    description\n    media\n    page {\n      ...PageFragment\n      __typename\n    }\n    criteoBrandAdIABInfo {\n      ...criteoInfoFragment\n      __typename\n    }\n    expressFilterAvailable\n    criteoBrandAdButterfly {\n      info {\n        ...criteoInfoFragment\n        __typename\n      }\n      onClickBeacon\n      onLoadBeacon\n      onViewBeacon\n      products {\n        ...CriteoButterflyProductFragment\n        __typename\n      }\n      __typename\n    }\n    criteoFormatBeaconInfo {\n      onViewBeacon\n      onClickBeacon\n      onLoadBeacon\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment productTileFragment on ProductBasicData {\n  productId\n  productPageUrl\n  categoryId\n  skuCode\n  productName\n  productDescription\n  brandName\n  unitSize\n  deal\n  unitPrice\n  weightDisclaimer\n  estimatedWeightDisclaimer\n  discountAmount {\n    ...priceFragment\n    __typename\n  }\n  salesUnits {\n    ...salesUnitFragment\n    __typename\n  }\n  price {\n    ...priceFragment\n    __typename\n  }\n  formattedCurrentPrice\n  roughPricePerUnit\n  defaultScaleUnit\n  pricePerScaleUnit\n  scaleUnit\n  servingSize\n  productZoomImage\n  productJumboImage\n  productAlternateImage\n  marketingTags {\n    soldOut\n    sponsored\n    yourFave\n    backOnline\n    new\n    __typename\n  }\n  featureTags {\n    topPick\n    freeSample\n    expressEligible\n    __typename\n  }\n  groupScale {\n    grpId\n    version\n    grpPrice\n    grpDescription\n    __typename\n  }\n  coupon {\n    ...couponFragment\n    __typename\n  }\n  wasPrice {\n    ...priceFragment\n    __typename\n  }\n  quantity {\n    ...productQuantityFragment\n    __typename\n  }\n  availability\n  available\n  alcoholic\n  preparationTime\n  savingString\n  availMaterialPrices {\n    price\n    pricingUnit\n    scaleLowerBound\n    scaleUpperBound\n    scaleUnit\n    promoPrice\n    __typename\n  }\n  cvPrices {\n    charName\n    charValueName\n    price\n    pricingUnit\n    applyHow\n    salesOrg\n    distChannel\n    __typename\n  }\n  grpPrices {\n    price\n    pricingUnit\n    scaleLowerBound\n    scaleUpperBound\n    scaleUnit\n    promoPrice\n    __typename\n  }\n  variantId\n  variations {\n    name\n    label\n    optional\n    display\n    underLabel\n    descrPopup\n    descrMedia\n    values {\n      name\n      label\n      isLabelValue\n      selected\n      cvp\n      imagePath\n      productName\n      description\n      variationItemProductData {\n        categoryId\n        productId\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n  externalData {\n    ...productExternalDataFragment\n    __typename\n  }\n  fdWinesAndSpirits\n  soldBySalesUnit\n  bundle {\n    ...productMealBundleFragment\n    __typename\n  }\n  configuration {\n    key\n    value\n    __typename\n  }\n  discountAmount {\n    ...priceFragment\n    __typename\n  }\n  clickBeacon\n  imageBeacon\n  viewBeacon\n  recommendedProduct {\n    productId\n    __typename\n  }\n  discontinuedSoon\n  __typename\n}\n\nfragment priceFragment on Price {\n  currency\n  value\n  formattedPrice\n  properties {\n    type\n    value\n    __typename\n  }\n  __typename\n}\n\nfragment salesUnitFragment on SalesUnit {\n  alternateSalesUnit\n  name\n  selected\n  salesUnit\n  ratio\n  __typename\n}\n\nfragment couponFragment on Coupon {\n  couponId\n  version\n  displayDescription\n  detailedDescription\n  value\n  quantity\n  expirationDate\n  offerType {\n    name\n    description\n    __typename\n  }\n  status {\n    name\n    description\n    displayMessage\n    __typename\n  }\n  displayStatus {\n    name\n    description\n    __typename\n  }\n  couponProductInfo {\n    catId\n    productId\n    skuCode\n    upc\n    __typename\n  }\n  displayStatusMessage\n  context {\n    name\n    description\n    __typename\n  }\n  __typename\n}\n\nfragment productQuantityFragment on ProductQuantity {\n  quantity\n  minQuantity\n  maxQuantity\n  quantityIncrement\n  __typename\n}\n\nfragment productExternalDataFragment on ProductExternalData {\n  externalWidgetId\n  externalWidgetType\n  externalResponseId\n  __typename\n}\n\nfragment productMealBundleFragment on Bundle {\n  type\n  variationGroups {\n    name\n    label\n    variations {\n      name\n      label\n      optional\n      optional\n      display\n      underLabel\n      descrPopup\n      descrMedia\n      marinadeData {\n        title\n        __typename\n      }\n      values {\n        name\n        label\n        isLabelValue\n        selected\n        cvp\n        productName\n        description\n        imagePath\n        variationItemProductData {\n          categoryId\n          productId\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment breadcrumbFragment on Breadcrumb {\n  id\n  value\n  url\n  __typename\n}\n\nfragment categoryFragment on Category {\n  id\n  name\n  url\n  childCount\n  __typename\n}\n\nfragment PageFragment on Page {\n  totalItems\n  page\n  size\n  count\n  firstOffset\n  lastOffset\n  __typename\n}\n\nfragment facetFragment on Facet {\n  id\n  name\n  detailName\n  type\n  selectionType\n  multiSelection\n  disabled\n  value {\n    ...facetValueFragment\n    __typename\n  }\n  primary\n  __typename\n}\n\nfragment facetValueFragment on FacetValue {\n  id\n  name\n  count\n  active\n  selected\n  __typename\n}\n\nfragment SortOptionFragment on SortOption {\n  id\n  name\n  selected\n  __typename\n}\n\nfragment CriteoButterflyProductFragment on CriteoProduct {\n  productData {\n    ...productBasicFragment\n    __typename\n  }\n  buttonName\n  desktopMultiBackground\n  isMandatory\n  onImageBeacon\n  onClickBeacon\n  onViewBeacon\n  __typename\n}\n\nfragment productBasicFragment on ProductBasicData {\n  listItemLineId\n  productId\n  productPageUrl\n  categoryId\n  deal\n  categoryPageUrl\n  skuCode\n  productName\n  akaName\n  brandName\n  packCount\n  unitSize\n  unitPrice\n  weightDisclaimer\n  estimatedWeightDisclaimer\n  salesUnits {\n    ...salesUnitFragment\n    __typename\n  }\n  price {\n    ...priceFragment\n    __typename\n  }\n  formattedCurrentPrice\n  roughPricePerUnit\n  defaultScaleUnit\n  pricePerScaleUnit\n  scaleUnit\n  servingSize\n  productImage\n  productDetailImage\n  productZoomImage\n  productJumboImage\n  productAlternateImage\n  productImagePackage\n  productDescription\n  productQualityNote\n  marketingTags {\n    soldOut\n    sponsored\n    yourFave\n    backOnline\n    new\n    __typename\n  }\n  featureTags {\n    topPick\n    freeSample\n    expressEligible\n    __typename\n  }\n  groupScale {\n    grpId\n    version\n    grpPrice\n    grpDescription\n    __typename\n  }\n  coupon {\n    ...couponFragment\n    __typename\n  }\n  wasPrice {\n    ...priceFragment\n    __typename\n  }\n  quantity {\n    ...productQuantityFragment\n    __typename\n  }\n  availability\n  available\n  alcoholic\n  preparationTime\n  savingString\n  availMaterialPrices {\n    price\n    pricingUnit\n    scaleLowerBound\n    scaleUpperBound\n    scaleUnit\n    promoPrice\n    __typename\n  }\n  cvPrices {\n    charName\n    charValueName\n    price\n    pricingUnit\n    applyHow\n    salesOrg\n    distChannel\n    __typename\n  }\n  grpPrices {\n    price\n    pricingUnit\n    scaleLowerBound\n    scaleUpperBound\n    scaleUnit\n    promoPrice\n    __typename\n  }\n  variantId\n  variations {\n    name\n    label\n    optional\n    display\n    underLabel\n    descrPopup\n    descrMedia\n    values {\n      name\n      label\n      isLabelValue\n      selected\n      cvp\n      imagePath\n      productName\n      description\n      variationItemProductData {\n        categoryId\n        productId\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n  externalData {\n    ...productExternalDataFragment\n    __typename\n  }\n  fdWinesAndSpirits\n  soldBySalesUnit\n  bundle {\n    ...productMealBundleFragment\n    __typename\n  }\n  configuration {\n    key\n    value\n    __typename\n  }\n  discountAmount {\n    ...priceFragment\n    __typename\n  }\n  clickBeacon\n  imageBeacon\n  viewBeacon\n  recommendedProduct {\n    productId\n    __typename\n  }\n  discontinuedSoon\n  __typename\n}\n\nfragment criteoInfoFragment on CriteoBrandAdIABResult {\n  backgroundImage\n  redirectUrl\n  redirectTarget\n  onClickBeacon\n  onLoadBeacon\n  onViewBeacon\n  selectedButtonColor\n  selectedButtonTextColor\n  buttonColor\n  buttonTextColor\n  optionalFooterText\n  optionalFooterBackgroundColor\n  optionalFooterTextColor\n  optionalFooterRedirectTarget\n  optionalFooterRedirectUrl\n  altTextBackgroundImage\n  __typename\n}"
    }])

    response = requests.post(url, headers=headers, data=payload)
    data = response.json()

    products = data[0]['data']['subcategorySearch']['products']

    if not products:
        printTrunc("No potato products found.")
    else:
        potato_data = []
        for product in products:
            name = product['productName']
            price = product['formattedCurrentPrice']
            potato_data.append([name, price])

        df = pd.DataFrame(potato_data, columns=["Product Name", "Price"])
        printTrunc(df.to_string())

except Exception as e:
    printTrunc(f"An error occurred: {e}")
