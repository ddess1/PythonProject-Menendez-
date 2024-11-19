from fastapi.testclient import TestClient
from app import app  # Импортируйте свой FastAPI app

client = TestClient(app)

def test_get_cars_with_filters():
    response = client.get("/cars?brand=Porshe&price_min=50000&price_max=100000")
    assert response.status_code == 200
    cars = response.json()
    assert isinstance(cars, list)  # Проверяем, что это список машин
    for car in cars:
        assert car["brand"] == "BMW"  # Проверяем, что бренд совпадает с запросом
        assert 50000 <= car["price"] <= 100000  # Проверяем, что цена в пределах диапазона

def test_get_cars_sorted_by_price():
    response = client.get("/cars?sort_by=price")
    assert response.status_code == 200
    cars = response.json()
    assert len(cars) > 0  # Проверяем, что машины есть
    prices = [car["price"] for car in cars]
    assert prices == sorted(prices)  # Проверяем, что список машин отсортирован по цене
