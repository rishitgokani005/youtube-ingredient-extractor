import cloudscraper
import requests

def test_blinkit():
    url = "https://blinkit.com/api/v2/products"
    headers = {
        "app_client": "consumer_web",
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json"
    }
    params = {"q": "onion", "start": 0, "size": 5}
    scraper = cloudscraper.create_scraper()
    try:
        res = scraper.get(url, headers=headers, params=params)
        print("Blinkit Status:", res.status_code)
        if res.status_code == 200:
            print("Blinkit Data Keys:", res.json().keys())
    except Exception as e:
        print("Blinkit Error:", e)

def test_bigbasket():
    url = "https://www.bigbasket.com/customsearch/getsearchresults/"
    headers = {
        "X-Requested-With": "XMLHttpRequest",
        "User-Agent": "Mozilla/5.0"
    }
    params = {"q": "onion"}
    scraper = cloudscraper.create_scraper()
    try:
        res = scraper.get(url, headers=headers, params=params)
        print("Bigbasket Status:", res.status_code)
        if res.status_code == 200:
            print("Bigbasket Data Keys:", list(res.json().keys()))
    except Exception as e:
        print("Bigbasket Error:", e)

test_blinkit()
test_bigbasket()
