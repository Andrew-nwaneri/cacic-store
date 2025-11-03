from models import db, Items


# --- Demo Inventory Data ---
inventory_data = [
    {
        "name": "Date Syrup",
        "description": "Made through controlled heating, blending, filtration and extraction. With no added colouring or preservatives it is a natural sugar that has the added benefit of being less processed than white sugar.",
        "img_url": "https://skinnyms.com/wp-content/uploads/2021/03/Homemade-Date-Syrup-1-Yum-500x500.jpg",
        "price": 15000.0,
        "unit": "Litre",
    },
    {
        "name": "Date Syrup (50CL)",
        "description": "Made through controlled heating, blending, filtration and extraction. With no added colouring or preservatives it's a natural sugar that has the added benefit of being less processed than white sugar.",
        "img_url": "https://m.media-amazon.com/images/I/713rSxKKaPL.jpg",
        "price": 7000.0,
        "unit": "50CL",
    },
    {
        "name": "Cat Fish",
        "description": "Vacuum dried fresh catfish, selectively sorted and dried under the perfect temperature, humidity and atmosphere to ensure the nutritional and hygienic qualities are maintained.",
        "img_url": "https://sc04.alicdn.com/kf/A83b0a6b2eb864b9d9fe9023c946cc3b8T.jpg",
        "price": 5000.0,
        "unit": "KG",
    },
    {
        "name": "Bag of Rice",
        "description": "Get value and quality with our 50 kg bag of rice. Ideal for bulk buying, this premium rice is perfect for everyday meals, catering, or large family use.",
        "img_url": "https://mall.thecbncoop.com/assets/images/products/1634569714Mama-choice---50-420x458.jpg",
        "price": 80500.0,
        "unit": "50KG",
    },
    {
        "name": "Groundnut Oil",
        "description": "Vegetable oil locally produced in Nigeria, well filtered, available in 25L kegs, hygienically packaged, and has a tamper-evident seal.",
        "img_url": "https://deeski.com/image/cache/catalog/Foods/Kings%20devon%20veg%20oil%2025ltrs-500x500.jpg",
        "price": 90500.0,
        "unit": "25Litre",
    },
    {
        "name": "Palm Oil",
        "description": "Palm oil locally produced in Nigeria, well filtered, available in 25L kegs, hygienically packaged, and has a tamper-evident seal.",
        "img_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcT6YNYp1jJXMOynawoAtkgEpaqOgtf9NOfcRQ&s",
        "price": 68500.0,
        "unit": "25Litre",
    },
]


# --- Seeder Function ---
def seed_demo_data():
    """Populate the demo database with sample products if empty."""
    existing = db.session.scalar(db.select(db.func.count(Items.id)))
    if existing and existing > 0:
        return  # Skip if already seeded

    demo_products = [Items(**item) for item in inventory_data]

    db.session.add_all(demo_products)
    db.session.commit()

    print(f"✅ Seeded {len(demo_products)} demo items into the database.")
