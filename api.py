from fastapi import FastAPI,HTTPException,Depends
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPBearer,HTTPAuthorizationCredentials
from pydantic import BaseModel,Field
from app.auth import hash_password,create_token,verify_token
from app.db import connect,init_db
app=FastAPI(title='Inventory & POS System API',version='4.0.0');init_db();security=HTTPBearer(auto_error=False)
products={};sales=[]
class Credentials(BaseModel):username:str=Field(min_length=3,max_length=80);password:str=Field(min_length=6,max_length=200)
class Product(BaseModel):sku:str=Field(min_length=1);name:str=Field(min_length=2);price:float=Field(gt=0);stock:int=Field(ge=0);reorder_level:int=Field(ge=0,default=5)
class SaleItem(BaseModel):sku:str;quantity:int=Field(gt=0)
class Sale(BaseModel):items:list[SaleItem]=Field(min_length=1)
def current_user(c:HTTPAuthorizationCredentials=Depends(security)):
    if not c:raise HTTPException(401,'Authentication required')
    u=verify_token(c.credentials)
    if not u:raise HTTPException(401,'Invalid or expired token')
    return u
@app.get('/health')
def health():return {'status':'ok','service':'inventory-pos-system','version':'4.0.0'}
@app.post('/auth/register')
def register(b:Credentials):
    with connect() as c:
        if c.execute('SELECT 1 FROM users WHERE username=?',(b.username,)).fetchone():raise HTTPException(409,'Username already exists')
        c.execute('INSERT INTO users(username,password_hash) VALUES(?,?)',(b.username,hash_password(b.password)));c.commit()
    return {'message':'registered','username':b.username}
@app.post('/auth/login')
def login(b:Credentials):
    with connect() as c:u=c.execute('SELECT * FROM users WHERE username=?',(b.username,)).fetchone()
    if not u or u['password_hash']!=hash_password(b.password):raise HTTPException(401,'Invalid username or password')
    return {'access_token':create_token(u['username']),'token_type':'bearer'}
@app.get('/auth/me')
def me(u=Depends(current_user)):return u
@app.post('/products')
def add_product(p:Product,u=Depends(current_user)):products[p.sku]=p.model_dump();return products[p.sku]
@app.get('/products')
def list_products(u=Depends(current_user)):return list(products.values())
@app.delete('/products/{sku}')
def delete_product(sku:str,u=Depends(current_user)):
    if sku not in products:raise HTTPException(404,'Product not found')
    return products.pop(sku)
@app.post('/checkout')
def checkout(s:Sale,u=Depends(current_user)):
    total=0;lines=[]
    for item in s.items:
        if item.sku not in products:raise HTTPException(404,f'Unknown SKU: {item.sku}')
        p=products[item.sku]
        if p['stock']<item.quantity:raise HTTPException(409,f'Insufficient stock for {item.sku}')
        total+=p['price']*item.quantity;lines.append({'sku':item.sku,'quantity':item.quantity,'unit_price':p['price']})
    for item in s.items:products[item.sku]['stock']-=item.quantity
    receipt={'id':len(sales)+1,'items':lines,'total':round(total,2),'user':u['username']};sales.append(receipt);return receipt
@app.get('/sales')
def list_sales(u=Depends(current_user)):return sales
@app.get('/dashboard')
def dashboard(u=Depends(current_user)):return {'products':len(products),'sales':len(sales),'revenue':round(sum(x['total'] for x in sales),2),'low_stock':[p for p in products.values() if p['stock']<=p['reorder_level']]}
app.mount('/',StaticFiles(directory='web',html=True),name='web')
