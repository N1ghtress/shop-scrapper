from requests_html import HTMLSession
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urlparse
import pandas as pd
import os

def get_urls(file_name):
    with open(file_name) as f:
        return [url for url in f]

def scrap_urls(urls):
    for url in urls:
        r = session.get(url)
        domain = urlparse(url).netloc                      
        if killswitches[domain]:
            domain_to_scrap_func[domain](r.html, fields)
                
def scrap_amazon(html, fields):
    product = html.find("#productTitle", first=True).text.strip(stripped)

    price_whole = html.find(".a-price-whole", first=True).text.strip(stripped) 
    price_fraction = html.find(".a-price-fraction", first=True).text.strip(stripped)
    price = int(price_whole) + int(price_fraction) / 100

    fields["products"].append(product)
    fields["prices"].append(price)
    
def scrap_cdiscount(html, fields):
    # Need javascript support somehow...
    html.render()
    product = html.find(".fpDesCol", first=True).text.strip(stripped)
    price = html.find(".fpPrice").attrs["content"]
    
    fields["products"].append(product)
    fields["prices"].append(price)
    
if __name__ == "__main__":
    os.environ['MOZ_HEADLESS'] = '1'
    stripped = "€., "
    fields = { 
        "products" : [],
        "prices" : []
    }
    killswitches = {
        "www.amazon.fr": True,
        "www.cdiscount.com": False
    }
    domain_to_scrap_func = {
        "www.amazon.fr": scrap_amazon,
        "www.cdiscount.com": scrap_cdiscount
    }
    datetime = datetime.now()
    session = HTMLSession()
    
    urls = get_urls("urls")
    scrap_urls(urls)

    df = pd.DataFrame({
        "Product name": fields["products"], 
        "Price": fields["prices"], 
        "Datetime": datetime
    })
    with open("products.csv", "a") as f:
        df.to_csv(f, header=False, index=False)
