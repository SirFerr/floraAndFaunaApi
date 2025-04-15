import requests

BASE_URL = "http://127.0.0.1:8000"

# 1. Регистрация
def register_user(email, password):
    response = requests.post(f"{BASE_URL}/register", params={"email": email, "password": password})
    print("Register:", response.status_code, response.json())

# 2. Логин
def login(email, password):
    response = requests.post(f"{BASE_URL}/token", data={"username": email, "password": password})
    print("Login:", response.status_code, response.json())
    return response.json().get("access_token")

# 3. Создание вида
def create_species(token):
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "name": "Белка",
        "scientific_name": "Sciurus vulgaris",
        "description": "Обыкновенная белка",
        "type": "fauna",
        "image_url": "https://example.com/squirrel.jpg"
    }
    response = requests.post(f"{BASE_URL}/species", params=payload, headers=headers)
    print("Create species:", response.status_code, response.json())

# 4. Поиск вида
def search_species(name):
    response = requests.get(f"{BASE_URL}/species/search", params={"name": name})
    print("Search:", response.status_code, response.json())

if __name__ == "__main__":
    email = "test@example.com"
    password = "secret123"

    register_user(email, password)
    token = login(email, password)

    if token:
        create_species(token)
        search_species("Белка")
