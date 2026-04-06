import os
import re
import random
import hashlib
import requests
from flask import Flask, render_template, request, jsonify
from yt_dlp import YoutubeDL

app = Flask(__name__)

TMP_DIR = "tmp_subs"
os.makedirs(TMP_DIR, exist_ok=True)

# Comprehensive ingredient keywords
COMMON_INGREDIENT_WORDS = [
    # Proteins
    "chicken", "beef", "pork", "lamb", "turkey", "duck", "fish", "salmon", "tuna", "shrimp", 
    "prawns", "crab", "lobster", "scallops", "mussels", "clams", "oysters", "ham", "bacon", 
    "sausage", "chorizo", "pepperoni", "tofu", "tempeh", "seitan", "eggs", "egg",
    
    # Dairy
    "milk", "cream", "butter", "cheese", "cheddar", "mozzarella", "parmesan", "feta", 
    "goat cheese", "ricotta", "cottage cheese", "yogurt", "sour cream", "buttermilk",
    "heavy cream", "half and half", "mascarpone", "cream cheese", "paneer",
    
    # Grains and starches
    "flour", "rice", "quinoa", "pasta", "noodles", "bread", "breadcrumbs", "oats", 
    "barley", "bulgur", "couscous", "polenta", "cornmeal", "cornstarch", "potato", 
    "potatoes", "sweet potato", "yam", "macaroni", "spaghetti", "linguine",
    
    # Vegetables
    "onion", "onions", "garlic", "tomato", "tomatoes", "carrot", "carrots", "celery", 
    "bell pepper", "peppers", "chili", "chilli", "jalapeño", "habanero", "serrano",
    "spinach", "kale", "lettuce", "arugula", "cabbage", "broccoli", "cauliflower",
    "zucchini", "eggplant", "cucumber", "radish", "beetroot", "turnip", "leek", "scallions",
    "green onions", "shallots", "mushrooms", "mushroom", "shiitake", "portobello",
    "asparagus", "artichoke", "avocado", "corn", "peas", "beans", "green beans",
    
    # Fruits
    "apple", "apples", "banana", "bananas", "lemon", "lemons", "lime", "limes", 
    "orange", "oranges", "grapefruit", "berries", "strawberries", "blueberries", 
    "raspberries", "blackberries", "grapes", "pineapple", "mango", "papaya", 
    "kiwi", "melon", "watermelon", "cantaloupe", "peach", "pear", "plum", "cherry",
    
    # Herbs and spices
    "salt", "pepper", "sugar", "basil", "oregano", "thyme", "rosemary", "sage", 
    "parsley", "cilantro", "coriander", "dill", "chives", "mint", "tarragon",
    "cumin", "paprika", "turmeric", "ginger", "cinnamon", "nutmeg", "cloves", 
    "cardamom", "star anise", "fennel", "bay leaf", "bay leaves", "vanilla",
    "saffron", "sumac", "za'atar", "curry powder", "garam masala", "chili powder",
    "cayenne", "black pepper", "white pepper", "red pepper flakes",
    
    # Liquids and oils
    "water", "oil", "olive oil", "vegetable oil", "canola oil", "coconut oil", 
    "sesame oil", "sunflower oil", "avocado oil", "vinegar", "balsamic vinegar", 
    "apple cider vinegar", "white vinegar", "rice vinegar", "wine vinegar",
    "broth", "stock", "chicken stock", "beef stock", "vegetable stock", "bone broth",
    "wine", "white wine", "red wine", "beer", "sake", "mirin", "coconut milk",
    
    # Pantry staples
    "honey", "maple syrup", "molasses", "brown sugar", "powdered sugar", "confectioners sugar",
    "baking powder", "baking soda", "yeast", "gelatin", "agar", "tahini", "peanut butter", 
    "almond butter", "jam", "jelly", "preserves", "mustard", "ketchup", "mayonnaise", 
    "soy sauce", "fish sauce", "worcestershire", "tabasco", "sriracha", "hot sauce", 
    "tomato paste", "tomato sauce", "coconut", "coconut flakes",
    
    # Nuts and seeds
    "almonds", "walnuts", "pecans", "hazelnuts", "pistachios", "cashews", "peanuts",
    "pine nuts", "macadamia", "brazil nuts", "sunflower seeds", "pumpkin seeds",
    "sesame seeds", "chia seeds", "flax seeds", "poppy seeds",
    
    # Legumes
    "black beans", "kidney beans", "pinto beans", "navy beans", "lima beans",
    "chickpeas", "garbanzo beans", "lentils", "red lentils", "green lentils", "split peas",
    
    # Specialty ingredients
    "chocolate", "cocoa powder", "dark chocolate", "white chocolate", "capers", "olives",
    "pickles", "anchovies", "sundried tomatoes", "roasted peppers", "artichoke hearts"

    #indian
      # Proteins
    "chicken", "beef", "pork", "lamb", "mutton", "turkey", "duck", "fish", "salmon", "tuna", "shrimp", 
    "prawns", "crab", "lobster", "scallops", "mussels", "clams", "oysters", "ham", "bacon", 
    "sausage", "chorizo", "pepperoni", "tofu", "tempeh", "seitan", "eggs", "egg",
    
    # Indian Dairy Products
    "milk", "cream", "butter", "cheese", "paneer", "ghee", "dahi", "yogurt", "curd", 
    "buttermilk", "chaas", "lassi", "khoya", "mawa", "rabri", "malai", "cream cheese",
    "cottage cheese", "cheddar", "mozzarella", "parmesan", "feta", "ricotta",
    "goat cheese", "sour cream", "heavy cream", "half and half", "mascarpone",
    
    # Indian Grains, Flours & Starches
    "flour", "rice", "basmati rice", "jasmine rice", "sona masoori", "quinoa", "pasta", "noodles", 
    "bread", "breadcrumbs", "oats", "barley", "bulgur", "couscous", "polenta", "cornmeal", 
    "cornstarch", "potato", "potatoes", "sweet potato", "yam", "macaroni", "spaghetti", "linguine",
    "atta", "maida", "wheat flour", "whole wheat flour", "besan", "gram flour", "chickpea flour",
    "rice flour", "sooji", "rava", "semolina", "poha", "beaten rice", "sabudana", "tapioca pearls",
    "vermicelli", "seviyaan", "upma rava", "ragi", "bajra", "jowar", "makki ka atta", "corn flour",
    
    # Indian Vegetables
    "onion", "onions", "garlic", "tomato", "tomatoes", "carrot", "carrots", "celery", 
    "bell pepper", "peppers", "capsicum", "shimla mirch", "chili", "chilli", "green chilli", 
    "red chilli", "jalapeño", "habanero", "serrano", "spinach", "palak", "kale", "lettuce", 
    "arugula", "cabbage", "patta gobi", "broccoli", "cauliflower", "phool gobi", "gobi",
    "zucchini", "eggplant", "brinjal", "baingan", "cucumber", "kheera", "radish", "mooli",
    "beetroot", "chukandar", "turnip", "shalgam", "leek", "scallions", "green onions", 
    "shallots", "mushrooms", "mushroom", "khumbi", "shiitake", "portobello", "asparagus",
    "artichoke", "avocado", "corn", "makki", "bhutta", "peas", "matar", "beans", "green beans",
    "french beans", "sem", "cluster beans", "guar", "drumstick", "moringa", "sahjan",
    "bottle gourd", "lauki", "ghiya", "ridge gourd", "tori", "bitter gourd", "karela",
    "snake gourd", "parwal", "pointed gourd", "ivy gourd", "tindora", "tendli",
    "lady finger", "okra", "bhindi", "pumpkin", "kaddu", "ash gourd", "petha",
    "lotus root", "kamal kakdi", "yam", "suran", "jimikand", "arbi", "colocasia",
    "raw banana", "kaccha kela", "plantain", "banana flower", "mochar",
    
    # Indian Fruits
    "apple", "apples", "banana", "bananas", "kela", "lemon", "lemons", "nimbu", 
    "lime", "limes", "orange", "oranges", "santra", "grapefruit", "berries", 
    "strawberries", "blueberries", "raspberries", "blackberries", "grapes", "angoor",
    "pineapple", "ananas", "mango", "aam", "papaya", "papita", "kiwi", "melon", 
    "watermelon", "tarbooj", "cantaloupe", "kharbuja", "peach", "aadu", "pear", "nashpati",
    "plum", "aloo bukhara", "cherry", "pomegranate", "anar", "guava", "amrood",
    "custard apple", "sitafal", "sharifa", "jackfruit", "kathal", "lychee", "litchi",
    "chickoo", "sapota", "jamun", "java plum", "black plum", "tamarind", "imli",
    "kokum", "amla", "indian gooseberry", "dates", "khajoor", "figs", "anjeer",
    
    # Indian Herbs & Leafy Greens
    "coriander", "cilantro", "dhaniya", "coriander leaves", "curry leaves", "kadi patta",
    "mint", "pudina", "fenugreek leaves", "methi", "kasuri methi", "dried fenugreek",
    "basil", "tulsi", "holy basil", "oregano", "thyme", "rosemary", "sage", 
    "parsley", "dill", "chives", "tarragon", "bay leaf", "bay leaves", "tej patta",
    "amaranth leaves", "chaulai", "mustard greens", "sarson ka saag", "bathua",
    
    # Indian Spices & Masalas (Comprehensive List)
    "salt", "namak", "pepper", "kali mirch", "black pepper", "white pepper", "sugar", "cheeni",
    "cumin", "jeera", "cumin seeds", "caraway seeds", "shahi jeera", "black cumin",
    "coriander seeds", "dhaniya", "sabut dhaniya", "mustard seeds", "sarson", "rai",
    "black mustard seeds", "yellow mustard seeds", "fenugreek seeds", "methi dana",
    "fennel seeds", "saunf", "carom seeds", "ajwain", "bishops weed", "celery seeds",
    "nigella seeds", "kalonji", "onion seeds", "black seeds", "poppy seeds", "khus khus",
    "sesame seeds", "til", "white sesame", "black sesame",
    
    # Whole Spices
    "cardamom", "elaichi", "green cardamom", "black cardamom", "badi elaichi",
    "cinnamon", "dalchini", "cloves", "laung", "star anise", "chakra phool",
    "mace", "javitri", "nutmeg", "jaiphal", "bay leaf", "tej patta",
    "stone flower", "dagad phool", "black stone flower", "patthar ke phool",
    "asafoetida", "hing", "dried mango powder", "amchur", "pomegranate seeds", "anardana",
    
    # Ground Spices & Powders
    "turmeric", "haldi", "turmeric powder", "red chilli powder", "lal mirch powder",
    "cayenne pepper", "kashmiri red chilli", "paprika", "coriander powder", "dhaniya powder",
    "cumin powder", "jeera powder", "black pepper powder", "kali mirch powder",
    "ginger powder", "saunth", "garlic powder", "onion powder", "fenugreek powder",
    "fennel powder", "saunf powder", "ajwain powder", "carom powder",
    
    # Indian Masala Blends
    "garam masala", "curry powder", "sambhar masala", "sambar powder", "rasam powder",
    "chaat masala", "pav bhaji masala", "biryani masala", "pulao masala",
    "tandoori masala", "tikka masala", "chicken masala", "mutton masala", "meat masala",
    "fish masala", "goda masala", "kala masala", "kolhapuri masala",
    "chana masala", "chole masala", "rajma masala", "kitchen king masala",
    "sabzi masala", "vegetable masala", "panch phoron", "panch puran",
    "tea masala", "chai masala", "ginger powder", "saunth",
    
    # Fresh Aromatics & Roots
    "ginger", "adrak", "garlic", "lehsun", "green chilli", "hari mirch",
    "curry leaves", "kadi patta", "fresh turmeric", "kachi haldi",
    
    # Indian Dals & Legumes
    "lentils", "dal", "toor dal", "arhar dal", "pigeon peas", "moong dal", "mung beans",
    "yellow moong dal", "green moong", "sabut moong", "masoor dal", "red lentils",
    "pink lentils", "urad dal", "black gram", "split black gram", "whole black gram",
    "sabut urad", "chana dal", "bengal gram", "chickpeas", "kabuli chana", "white chickpeas",
    "kala chana", "black chickpeas", "garbanzo beans", "rajma", "kidney beans",
    "red kidney beans", "white kidney beans", "black beans", "pinto beans", "navy beans",
    "lima beans", "green lentils", "split peas", "matar dal", "moth beans", "matki",
    "horse gram", "kulthi dal", "black eyed peas", "lobia", "cowpeas",
    
    # Indian Oils & Fats
    "oil", "tel", "ghee", "clarified butter", "mustard oil", "sarson ka tel",
    "coconut oil", "nariyal tel", "groundnut oil", "peanut oil", "moongfali ka tel",
    "sesame oil", "til ka tel", "vegetable oil", "sunflower oil", "soybean oil",
    "olive oil", "canola oil", "rice bran oil", "avocado oil", "butter", "makhan",
    
    # Indian Condiments & Sauces
    "tamarind", "imli", "tamarind paste", "tamarind pulp", "kokum", "dried kokum",
    "vinegar", "sirka", "malt vinegar", "white vinegar", "apple cider vinegar",
    "soy sauce", "tomato sauce", "tomato ketchup", "green chutney", "red chutney",
    "mint chutney", "coriander chutney", "coconut chutney", "peanut chutney",
    "tamarind chutney", "date chutney", "pickle", "achar", "mango pickle",
    "lemon pickle", "mixed pickle", "papad", "papadum", "chutney powder",
    
    # Indian Sweeteners & Sugars
    "sugar", "cheeni", "jaggery", "gur", "brown sugar", "khand", "mishri", "rock sugar",
    "honey", "shahad", "maple syrup", "molasses", "gudh", "palm jaggery", "karupatti",
    "date sugar", "coconut sugar", "powdered sugar", "icing sugar", "bura sugar",
    
    # Indian Nuts & Seeds (Extended)
    "cashews", "kaju", "almonds", "badam", "pistachios", "pista", "walnuts", "akhrot",
    "peanuts", "moongfali", "groundnuts", "charoli", "chironji", "melon seeds", "magaz",
    "watermelon seeds", "fox nuts", "makhana", "lotus seeds", "pine nuts", "chilgoza",
    "pecans", "hazelnuts", "macadamia", "brazil nuts", "sunflower seeds", "surajmukhi",
    "pumpkin seeds", "kaddu ke beej", "chia seeds", "flax seeds", "alsi", "linseed",
    
    # Indian Flours & Batters
    "idli batter", "dosa batter", "dhokla flour", "pakora flour", "bhajiya flour",
    
    # Indian Beverages & Liquids
    "water", "pani", "coconut water", "nariyal pani", "buttermilk", "chaas", "lassi",
    "coconut milk", "nariyal ka doodh", "almond milk", "tea", "chai", "coffee",
    "rose water", "gulab jal", "kewra water", "kewra essence", "screwpine water",
    "broth", "stock", "chicken stock", "vegetable stock", "bone broth",
    
    # Indian Specialty Ingredients
    "paneer", "khoya", "mawa", "chenna", "rabri", "condensed milk", "evaporated milk",
    "saffron", "kesar", "vanilla", "vanilla essence", "cardamom powder", "rose essence",
    "paan", "betel leaf", "betel nut", "supari", "edible camphor", "kapur",
    "silver leaf", "vark", "varq", "edible silver foil", "gold leaf", "edible gold",
    "food color", "food coloring", "baking powder", "baking soda", "meetha soda",
    "yeast", "khameera", "gelatin", "agar agar", "china grass", "cornflour",
    "arrowroot powder", "sago", "sabudana", "vermicelli", "seviyan",
    
    # International ingredients (kept for versatility)
    "pasta", "noodles", "spaghetti", "macaroni", "cheese", "chocolate", "cocoa powder",
    "olives", "capers", "worcestershire sauce", "tabasco", "sriracha", "hot sauce",
    "mustard", "mayonnaise", "tahini", "peanut butter", "almond butter", "jam", "jelly"
]


def clean_vtt_text_to_lines(vtt_text: str):
    """Extract and clean text lines from VTT subtitle file."""
    text = vtt_text

    # Remove WEBVTT header
    text = re.sub(r'^\s*WEBVTT.*\n', '', text, flags=re.IGNORECASE)

    # Remove STYLE or NOTE blocks
    text = re.sub(r'(?:STYLE|NOTE).*?(?:\n\n|$)', '', text, flags=re.DOTALL | re.IGNORECASE)

    # Remove cue timestamp lines
    text = re.sub(r'^\s*\d{2}:\d{2}:\d{2}(?:\.\d+)?\s*-->\s*\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:.*)?\s*$',
                  '', text, flags=re.MULTILINE)

    # Remove angle-bracket tags
    text = re.sub(r'<[^>]+>', '', text)

    # Process lines
    lines = []
    for ln in text.splitlines():
        ln = ln.strip()
        if not ln or re.fullmatch(r'\d+', ln):
            continue
        
        ln = re.sub(r'\s+', ' ', ln)
        lines.append(ln)

    # Deduplicate
    seen = set()
    dedup = []
    for l in lines:
        key = l.lower().strip()
        if key not in seen:
            seen.add(key)
            dedup.append(l)
            
    return dedup

def is_ingredient_line(line):
    """Determine if a line is likely talking about ingredients."""
    line_lower = line.lower().strip()
    words = line_lower.split()
    
    if not line_lower or len(words) == 0 or len(words) > 15:
        return False
    
    # Check for instruction indicators
    instruction_indicators = [
        "preheat", "bake", "fry", "cook", "stir", "mix", "combine", "whisk",
        "minute", "hour", "degree", "temperature", "oven", "pan", "pot",
        "video", "channel", "subscribe", "like", "comment", "today", "hello", "welcome"
    ]
    
    for indicator in instruction_indicators:
        if indicator in line_lower:
            return False
    
    # Must contain at least one known ingredient
    for ingredient in COMMON_INGREDIENT_WORDS:
        if re.search(r'\b' + re.escape(ingredient) + r'\b', line_lower):
            return True
    
    return False

def is_definitely_ingredient(text):
    """Ultra-strict validation that text is definitely a food ingredient."""
    text_lower = text.lower().strip()
    
    if len(text_lower) < 2:
        return False
    
    # Absolute rejection list
    absolute_rejects = [
        "cook", "bake", "fry", "heat", "stir", "mix", "add", "combine",
        "minute", "hour", "degree", "temperature", "pan", "pot", "oven",
        "video", "channel", "today", "hello", "welcome", "recipe", "going",
        "just", "says", "right", "we'll", "do", "friends", "leaf"
    ]
    
    for word in text_lower.split():
        if word in absolute_rejects:
            return False
    
    # Must contain a known ingredient
    for ingredient in COMMON_INGREDIENT_WORDS:
        if re.search(r'\b' + re.escape(ingredient) + r'\b', text_lower):
            return True
    
    return False

def extract_ingredients_from_line(line):
    """Extract ONE validated ingredient from a line."""
    line_lower = line.lower()
    
    # Find the best ingredient
    best_ingredient = None
    best_score = 0
    best_position = len(line)
    
    for ingredient in COMMON_INGREDIENT_WORDS:
        pattern = r'\b' + re.escape(ingredient) + r'\b'
        match = re.search(pattern, line_lower)
        
        if match:
            score = len(ingredient) - (match.start() / 10)
            if score > best_score and match.start() < best_position:
                best_ingredient = ingredient
                best_score = score
                best_position = match.start()
    
    if not best_ingredient or not is_definitely_ingredient(best_ingredient):
        return []
    
    ingredient_name = best_ingredient.strip().title()
    
    return [ingredient_name]

def extract_structured_ingredients(lines):
    """Extract ingredients from lines."""
    all_ingredients = []
    
    for line in lines:
        if is_ingredient_line(line):
            ingredients = extract_ingredients_from_line(line)
            all_ingredients.extend(ingredients)
    
    # Remove duplicates while preserving order
    seen = set()
    unique = []
    for ing in all_ingredients:
        key = ing.lower()
        if key not in seen:
            seen.add(key)
            unique.append(ing)
    
    return unique

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/extract', methods=['POST'])
def extract():
    data = request.get_json() or {}
    url = (data.get('youtube_url') or "").strip()
    if not url:
        return jsonify({"error": "Missing youtube_url"}), 400

    ydl_opts = {
        'skip_download': True,
        'writesubtitles': True,
        'writeautomaticsub': True,
        'subtitleslangs': ['en'],
        'subtitlesformat': 'vtt',
        'outtmpl': os.path.join(TMP_DIR, '%(id)s.%(ext)s'),
        'quiet': False,
        'no_warnings': False,
        'ignoreerrors': True,
        'extract_flat': False,
        'format': 'worst',
        'noplaylist': True,
    }

    vid_id = None
    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            vid_id = info.get('id')
            
            if not info.get('subtitles') and not info.get('automatic_captions'):
                return jsonify({"error": "No subtitles available for this video."}), 404
            
            ydl.download([url])
            
    except Exception as e:
        error_msg = str(e)
        error_msg = re.sub(r'\x1b\[[0-9;]*m', '', error_msg)
        return jsonify({"error": f"yt-dlp failed: {error_msg}"}), 500

    if not vid_id:
        return jsonify({"error": "Could not extract video ID"}), 500

    try:
        files = [f for f in os.listdir(TMP_DIR) if f.startswith(vid_id) and f.lower().endswith('.vtt')]
    except FileNotFoundError:
        return jsonify({"error": "Subtitle directory not found"}), 500
    
    if not files:
        return jsonify({"error": "No subtitle files were downloaded. The video may not have English subtitles."}), 404
    
    files_en = [f for f in files if '.en.' in f.lower() or f.lower().endswith('.en.vtt')]
    chosen = files_en[0] if files_en else files[0]
    chosen = os.path.join(TMP_DIR, chosen)

    try:
        with open(chosen, 'r', encoding='utf-8') as fh:
            raw = fh.read()
    except Exception as e:
        return jsonify({"error": f"Failed to read subtitle file: {e}"}), 500

    lines = clean_vtt_text_to_lines(raw)
    ingredients = extract_structured_ingredients(lines)
    
    print(f"DEBUG: Found {len(ingredients)} ingredients: {ingredients}")

    # Cleanup
    for f in [f for f in os.listdir(TMP_DIR) if f.startswith(vid_id) and f.lower().endswith('.vtt')]:
        try:
            os.remove(os.path.join(TMP_DIR, f))
        except Exception:
            pass

    return jsonify({"video_id": vid_id, "ingredients": ingredients})

def get_base_price(ingredient):
    # Generates a consistent base price for an ingredient between 30 and 400 INR
    seed = int(hashlib.md5(ingredient.lower().encode('utf-8')).hexdigest(), 16)
    random.seed(seed)
    return random.randint(30, 400)

def get_flashmart_product(ingredient):
    """Attempt to fetch real product data from local FlashMart server."""
    try:
        # Search for the ingredient in FlashMart's product database
        # Use suggestions endpoint as it uses regex search for better accuracy
        response = requests.get(
            "http://localhost:5000/api/products/search/suggestions", 
            params={"q": ingredient},
            timeout=1 # Quick timeout to prevent stalling if server is offline
        )
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and data.get('data'):
                # Take the first matching product (most accurate match)
                return data['data'][0]
    except Exception:
        pass # Silent fail to allow fallback to mock data
    return None



@app.route('/get_prices', methods=['POST'])
def get_prices():
    data = request.get_json() or {}
    ingredients = data.get('ingredients', [])
    
    if not ingredients:
        return jsonify({"error": "No ingredients provided"}), 400
        
    apps = ["FlashMart"]
    results = {app_name: [] for app_name in apps}
    
    for ing in ingredients:
        # FlashMart real fetch
        real_flash_product = get_flashmart_product(ing)
        if real_flash_product:
            results["FlashMart"].append({
                "ingredient": ing,
                "product_name": real_flash_product.get('name'),
                "price": real_flash_product.get('price'),
                "quantity": real_flash_product.get('unit', '1 unit'),
                "in_stock": real_flash_product.get('stock', 0) > 0,
                "is_real": True,
                "productId": str(real_flash_product.get('_id'))
            })
            
    return jsonify({"prices": results})

if __name__ == '__main__':
    app.run(debug=True)