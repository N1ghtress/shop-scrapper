from requests_html import HTMLSession
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urlparse
import pandas as pd
import os

def get_urls(file_name):
    with open(file_name) as f:
        return [url for url in f]

def scrap_urls(urls, fields):
    for url in urls:
        r = session.get(url)
        domain = urlparse(url).netloc                 
        if killswitches[domain]:
            print(f"Requesting ... {domain}")
            product, price = domain_to_scrap_func[domain](r.html, fields)
            fields["products"].append(product)
            fields["prices"].append(price)
            fields["datetimes"].append(datetime.now())
                
def scrap_amazon(html, fields):
    # Sometimes doesn't work, Samsung 970 EVO SSD NVMe 2To
    product = html.find(".product-title-word-break", first=True)
    if product:
        product = product.text.strip(stripped)
    
    price_whole = html.find(".a-price-whole", first=True)
    if price_whole:
        price_whole = price_whole.text.strip(stripped) 
    price_fraction = html.find(".a-price-fraction", first=True)
    if price_fraction:
        price_fraction = price_fraction.text.strip(stripped)
    price = None
    if price_whole and price_fraction:
        price = int(price_whole) + int(price_fraction) / 100
    
    return (product, price)
    
def scrap_cdiscount(html, fields):
    # Need javascript support somehow...
    html.render()
    product = html.find(".fpDesCol", first=True)
    if product:
        product = product.text.strip(stripped)
    price = html.find(".fpPrice")
    if price:
        price = price.attrs["content"]
    
    return (product, price)

def scrap_decathlon(html, fields):
    product = html.find("h1", first=True)
    if product:
        product = product.text.strip(stripped)
    price = html.find(".prc__active-price", first=True)
    if price:
        price = price.attrs["content"]

    return (product, price)
        
if __name__ == "__main__":
    stripped = "€., "
    fields = {
        "products": [],
        "prices":  [],
        "datetimes": []
    }
    killswitches = {
        "www.amazon.fr": True,
        "www.cdiscount.com": False,
        "www.decathlon.fr": True
    }
    domain_to_scrap_func = {
        "www.amazon.fr": scrap_amazon,
        "www.cdiscount.com": scrap_cdiscount,
        "www.decathlon.fr": scrap_decathlon
    }
    datetime = datetime.now()
    session = HTMLSession()
    
    urls = get_urls("urls")
    scrap_urls(urls, fields)

    df = pd.DataFrame({
        "Product name": fields["products"], 
        "Price": fields["prices"], 
        "Datetime": fields["datetimes"]
    })
    with open("products.csv", "a") as f:
        df.to_csv(f, header=False, index=False)
