from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app=FastAPI(title='Inventory & POS API',version='1.0.0')
products={}; sales=[]
class Product(BaseModel): sku:str; name:str; price:float=Field(gt=0); stock:int=Field(ge=0); reorder_level:int=Field(ge=0,default=5)
class SaleItem(BaseModel): sku:str; quantity:int=Field(gt=0)
class Sale(BaseModel): items:list[SaleItem]
@app.get('/health')
def health(): return {'status':'ok','service':'inventory-pos-system'}
@app.post('/products')
def add_product(p:Product): products[p.sku]=p.model_dump(); return products[p.sku]
@app.get('/products')
def list_products(): return list(products.values())
@app.post('/checkout')
def checkout(s:Sale):
    total=0; lines=[]
    for item in s.items:
        if item.sku not in products: raise HTTPException(404,f'Unknown SKU: {item.sku}')
        p=products[item.sku]
        if p['stock']<item.quantity: raise HTTPException(409,f'Insufficient stock for {item.sku}')
        total+=p['price']*item.quantity; lines.append({'sku':item.sku,'quantity':item.quantity,'unit_price':p['price']})
    for item in s.items: products[item.sku]['stock']-=item.quantity
    receipt={'id':len(sales)+1,'items':lines,'total':round(total,2)}; sales.append(receipt); return receipt
@app.get('/dashboard')
def dashboard(): return {'products':len(products),'sales':len(sales),'revenue':round(sum(x['total'] for x in sales),2),'low_stock':[p for p in products.values() if p['stock']<=p['reorder_level']]}
