import requests

BASE_URL = "http://127.0.0.1:8000"

# Регистрация пользователя
def register():
    response = requests.post(f"{BASE_URL}/register", params={
        "email": "test@example.com",
        "password": "secret"
    })
    print("Register:", response.status_code, response.json())

# Авторизация
def login():
    response = requests.post(f"{BASE_URL}/token", data={
        "username": "test@example.com",
        "password": "secret"
    })
    print("Login:", response.status_code, response.json())
    return response.json().get("access_token")

# Создание вида
def create_species(token):
    response = requests.post(f"{BASE_URL}/species", params={
        "name": "Ель",
        "scientific_name": "Picea abies",
        "description": "Хвойное дерево",
        "is_flora": True,
        "image_url": "http://example.com/image.jpg"
    }, headers={"Authorization": f"Bearer {token}"})
    print("Create species:", response.status_code, response.json())

# Поиск вида
def search_species():
    response = requests.get(f"{BASE_URL}/species/search", params={
        "name": "Ель"
    })
    print("Search species:", response.status_code, response.json())

# Получить все виды
def list_species():
    response = requests.get(f"{BASE_URL}/species")
    print("All species:", response.status_code, response.json())

# Запуск тестов
if __name__ == "__main__":
    register()
    token = login()
    if token:
        create_species(token)
    search_species()
    list_species()
