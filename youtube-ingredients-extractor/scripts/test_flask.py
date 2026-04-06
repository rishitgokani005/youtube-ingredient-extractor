import requests

try:
    res = requests.post("http://localhost:5001/get_prices", json={"ingredients": ["onion", "chicken"]})
    print(res.status_code)
    try:
        import pprint
        pprint.pprint(res.json())
    except Exception:
        print(res.text)
except Exception as e:
    print("Flask app not running at 5001 or error:", e)
