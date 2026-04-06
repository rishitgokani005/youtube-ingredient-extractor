import requests

def test_flashmart_search(ingredient):
    url = "http://localhost:5000/api/products"
    params = {"search": ingredient}
    try:
        response = requests.get(url, params=params, timeout=2)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                products = data.get('data', [])
                print(f"Found {len(products)} products for '{ingredient}'")
                for p in products:
                    cat = p.get('category', {})
                    cat_name = cat.get('name') if isinstance(cat, dict) else 'N/A'
                    print(f" - {p.get('name')} (Category: {cat_name})")
            else:
                print("API call failed (success=False)")
        else:
            print(f"HTTP Error: {response.status_code}")
    except Exception as e:
        print(f"Error connecting to FlashMart: {e}")

if __name__ == "__main__":
    test_flashmart_search("cream")
    test_flashmart_search("onion")
