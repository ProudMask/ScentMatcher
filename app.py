from flask import Flask, request, jsonify

app = Flask(__name__)

# Sample perfume data (you should use a database in a real application)
perfumes = [
    {
        "name": "Dior Blooming Bouquet",
        "brand": "Dior",
        "notes": "Floral, Citrus",
        "price": 100,
        "reviews": ["Lovely scent!", "Lasts all day."]
    },
    # Add more perfume data here
]

@app.route('/search', methods=['POST'])
def search_perfumes():
    user_input = request.json.get('perfume_name')
    
    # Sample matching logic (you should refine this)
    matches = []
    for perfume in perfumes:
        if user_input.lower() in perfume["name"].lower():
            matches.append(perfume)
    
    return jsonify(matches)

if __name__ == '__main__':
    app.run(debug=True)
