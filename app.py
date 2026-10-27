import os
import base64
import requests
from flask import Flask, render_template, request, redirect, url_for
from PIL import Image
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Exhaustive visual library for waste craft possibilities
UPCYCLE_DATABASE = {
    'Plastic': {
        'title': 'Plastic Bottle & Container Designs',
        'materials': ['Scissors', 'Utility Knife', 'Non-toxic paint / markers', 'Twine or glue'],
        'projects': [
            {
                'id': 'p1',
                'title': 'Intricate Pet Planter',
                'description': 'Upcycle a bottom half into a cute pet-faced planter.',
                'image_url': 'https://images.unsplash.com/photo-1599599810769-bcde5a160d32?auto=format&fit=crop&q=80&w=400',
                'steps': [
                    'Cut the bottom third of a plastic bottle, leaving 2 ear shapes.',
                    'Paint the entire exterior white or your choice of base color.',
                    'After it dries, paint eyes, nose, and whiskers to resemble a pet face.',
                    'Punch tiny drainage holes in the bottom.',
                    'Add soil and plant a small succulent or herb.'
                ]
            },
            {
                'id': 'p2',
                'title': 'Garden Bird Feeder',
                'description': 'Provide food for local birds using a bottle and spoons.',
                'image_url': 'https://images.unsplash.com/photo-1549608276-5ca80d6232b5?auto=format&fit=crop&q=80&w=400',
                'steps': [
                    'Clean a plastic bottle and dry it completely.',
                    'Cut two pairs of holes on opposite sides to insert wooden spoons.',
                    'Slip the spoons through; they will act as perches and feed catchers.',
                    'Fill the bottle with bird seed.',
                    'Tightly wrap wire around the cap or neck to hang from a branch.'
                ]
            },
            {
                'id': 'p3',
                'title': 'Eco Hanging Lantern',
                'description': 'Cut designs on the bottle and insert LED candle lights.',
                'image_url': 'https://images.unsplash.com/photo-1513519245088-0e12902e5a38?auto=format&fit=crop&q=80&w=400',
                'steps': [
                    'Gently cut patterns or spiral slices into the bottle center.',
                    'Affix decorative paper, ribbons, or eco-safe colors.',
                    'Bore a small hole at the base to feed an LED fairy wire or LED tea candle.',
                    'Hang safely in indoor/outdoor spaces.'
                ]
            }
        ]
    },
    'Glass': {
        'title': 'Glass Jar & Bottle Upcycles',
        'materials': ['Pebbles', 'Charcoal', 'Brush', 'Twine', 'Glass paint'],
        'projects': [
            {
                'id': 'g1',
                'title': 'Micro Terrarium',
                'description': 'Create a mini self-sustaining plant ecosystem.',
                'image_url': 'https://images.unsplash.com/photo-1463936575829-25148e1db1b8?auto=format&fit=crop&q=80&w=400',
                'steps': [
                    'Sanitize the interior of a glass jar.',
                    'Spread pebbles at the bottom for drainage, followed by a bit of activated charcoal.',
                    'Add potting soil on top.',
                    'Plant small succulents or moss using long tweezers.',
                    'Lightly mist with water and seal or leave open depending on the plant.'
                ]
            }
        ]
    },
    'Cardboard': {
        'title': 'Cardboard Organizer Crafts',
        'materials': ['Box cutter', 'Wrapping paper/glue', 'Ruler', 'Adhesives'],
        'projects': [
            {
                'id': 'c1',
                'title': 'Compartment Desk Organizer',
                'description': 'Custom desk storage from boxes and tubes.',
                'image_url': 'https://images.unsplash.com/photo-1583847268964-b28dc8f51f92?auto=format&fit=crop&q=80&w=400',
                'steps': [
                    'Identify 1 sturdy outer box and several smaller boxes/cylinders.',
                    'Wrap or paint each individual component.',
                    'Organize the tubes and small sections inside the larger box.',
                    'Glue them securely to the base and side walls.',
                    'Use to hold pencils, brushes, and desk supplies.'
                ]
            }
        ]
    },
    'Cloth': {
        'title': 'Fabric & Old Clothing Crafts',
        'materials': ['Scissors', 'Sewing kit/glue', 'Safety pins'],
        'projects': [
            {
                'id': 'cl1',
                'title': 'Upcycled Canvas Tote',
                'description': 'Create an eco shopping bag from an old T-shirt.',
                'image_url': 'https://images.unsplash.com/photo-1544816155-12df9643f363?auto=format&fit=crop&q=80&w=400',
                'steps': [
                    'Lay the old shirt flat on a desk.',
                    'Cut off the sleeves and scoop the neck to form handles.',
                    'Turn the shirt inside out.',
                    'Sew the bottom hem shut or tie the fringe bottom into tight double knots.',
                    'Flip it back and your reusable tote is ready.'
                ]
            }
        ]
    },
    'Paper': {
        'title': 'Paper & Cardboard Utility Designs',
        'materials': ['Paper trimmer', 'Mod Podge/glue', 'Brushes'],
        'projects': [
            {
                'id': 'pa1',
                'title': 'Woven Paper Storage Basket',
                'description': 'Roll and weave newspapers or scraps into handy bins.',
                'image_url': 'https://images.unsplash.com/photo-1533867617858-e7b97e060509?auto=format&fit=crop&q=80&w=400',
                'steps': [
                    'Tightly roll several paper sheets into thin rods, securing ends with glue.',
                    'Arrange a series of rods horizontally and vertically on cardboard for the base.',
                    'Weave other paper rods in and out through the base rods to build up the wall.',
                    'Apply a mixture of glue and water (or Mod Podge) to strengthen.',
                    'Tuck and glue top edges inward.'
                ]
            }
        ]
    },
    'Straws': {
        'title': 'Straw Structure Designs',
        'materials': ['Glue gun', 'Scissors', 'Light wire', 'Paint'],
        'projects': [
            {
                'id': 'st1',
                'title': 'Decorative Geometric Mobile',
                'description': 'Make modern hanging sculptures.',
                'image_url': 'https://images.unsplash.com/photo-1502086223501-7ea6ecd79368?auto=format&fit=crop&q=80&w=400',
                'steps': [
                    'Cut waste straws into equal 3-4 inch segments.',
                    'Thread wire or strong string through them to create triangular units.',
                    'Connect multiple triangles to form 3D geometric shapes.',
                    'Add painted elements or hang on a mobile support.',
                    'Suspend from the ceiling as contemporary decor.'
                ]
            }
        ]
    },
    'Default': {
        'title': 'General Material DIY Crafts',
        'materials': ['Basic workspace tools', 'Safe adhesives'],
        'projects': [
            {
                'id': 'd1',
                'title': 'Eco Storage Bin',
                'description': 'Decorate and repurpose any safe industrial or house container.',
                'image_url': 'https://images.unsplash.com/photo-1585255318113-4cb8e4ba4367?auto=format&fit=crop&q=80&w=400',
                'steps': [
                    'Ensure the item is completely cleaned and dried.',
                    'Assess your extra safe scrap pieces for customization.',
                    'Coat or cover the surface using paper, paint, or cloth.',
                    'Delineate segments using partition strips.',
                    'Utilize for organized household or workspace storage.'
                ]
            }
        ]
    }
}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    if 'material_image' not in request.files:
        return redirect(request.url)
    
    file = request.files['material_image']
    if file.filename == '':
        return redirect(url_for('home'))

    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filepath)

    try:
        img = Image.open(filepath).convert('RGB')
        temp_jpg = os.path.join(app.config['UPLOAD_FOLDER'], 'temp_upload.jpg')
        img.save(temp_jpg, format="JPEG")
        
        with open(temp_jpg, "rb") as img_file:
            img_b64 = base64.b64encode(img_file.read()).decode('utf-8')
        
        # Guide the AI to give highly specific materials for accurate dynamic matching
        prompt = "Analyze this image. Output exactly two lines. Line 1: Broad category (choose ONLY one exact word from: Plastic, Glass, Cardboard, Paper, Cloth, Straws, or Default). Line 2: Specific item name in 1 to 3 words max (e.g., Plastic Water Bottle, Cardboard Box, Glass Jar, Straws, Cloth T-shirt)."
        
        url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": GEMINI_API_KEY 
        }
        payload = {
            "contents": [{
                "parts": [
                    {"text": prompt},
                    {"inlineData": {"mimeType": "image/jpeg", "data": img_b64}}
                ]
            }]
        }
        
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
            
        data = response.json()
        result_text = data['candidates'][0]['content']['parts'][0]['text']
        
        lines = result_text.strip().split('\n')
        broad_category = lines[0].replace('Line 1:', '').strip()
        specific_name = lines[1].replace('Line 2:', '').strip().title()
        
        if broad_category not in UPCYCLE_DATABASE:
            broad_category = 'Default'

    except Exception as e:
        print(f"Server Error: {e}")
        # Soft fallback so the app stays up and running
        broad_category = 'Default'
        specific_name = "Eco Material"

    return render_template('result.html', category=broad_category, material=specific_name, image_path=url_for('static', filename=f"uploads/{file.filename}"))

@app.route('/recycle/<category>')
def recycle_ideas(category):
    # Match the broad prediction to our high-quality custom static gallery
    category_data = UPCYCLE_DATABASE.get(category, UPCYCLE_DATABASE['Default'])
    return render_template('recycle.html', category=category, material_title=category_data['title'], data=category_data)

@app.route('/dispose/<category>')
def dispose_guide(category):
    return render_template('dispose.html', material=category)

if __name__ == '__main__':
    app.run(debug=True)