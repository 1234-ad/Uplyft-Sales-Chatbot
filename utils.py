import random

product_names = ["Laptop", "Headphones", "Keyboard", "Monitor", "Mouse", "Webcam", "Router", "Printer", "Tablet", "Smartphone"]

def generate_mock_products():
    mock_products = []
    for i in range(1, 101):
        name = random.choice(product_names) + f" Model {i}"
        description = f"This is the description for {name}."
        price = round(random.uniform(20, 2000), 2)
        mock_products.append({
            "name": name,
            "description": description,
            "price": price
        })
    return mock_products
