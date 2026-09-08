from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

app=FastAPI(title='Inventory & POS System API',version='2.0.0')
products={}; sales=[]
class Product(BaseModel): sku:str=Field(min_length=1); name:str=Field(min_length=2); price:float=Field(gt=0); stock:int=Field(ge=0); reorder_level:int=Field(ge=0,default=5)
class SaleItem(BaseModel): sku:str; quantity:int=Field(gt=0)
class Sale(BaseModel): items:list[SaleItem]=Field(min_length=1)
@app.get('/health')
def health(): return {'status':'ok','service':'inventory-pos-system','version':'2.0.0'}
@app.post('/products')
def add_product(p:Product): products[p.sku]=p.model_dump(); return products[p.sku]
@app.get('/products')
def list_products(): return list(products.values())
@app.delete('/products/{sku}')
def delete_product(sku:str):
    if sku not in products: raise HTTPException(404,'Product not found')
    return products.pop(sku)
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
@app.get('/sales')
def list_sales(): return sales
@app.get('/dashboard')
def dashboard(): return {'products':len(products),'sales':len(sales),'revenue':round(sum(x['total'] for x in sales),2),'low_stock':[p for p in products.values() if p['stock']<=p['reorder_level']]}
app.mount('/',StaticFiles(directory='web',html=True),name='web')
