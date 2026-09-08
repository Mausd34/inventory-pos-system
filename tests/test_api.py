from fastapi.testclient import TestClient
from api import app
client=TestClient(app)
def test_health(): assert client.get('/health').status_code==200
def test_checkout():
    client.post('/products',json={'sku':'SKU-1','name':'Demo','price':10,'stock':5,'reorder_level':1})
    r=client.post('/checkout',json={'items':[{'sku':'SKU-1','quantity':2}]})
    assert r.status_code==200 and r.json()['total']==20
