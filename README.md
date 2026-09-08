# Inventory & POS System

A professional small-business inventory and point-of-sale backend with product management, checkout, stock validation, low-stock alerts, and sales metrics.

## Features
- Product/SKU catalog
- Stock management and low-stock alerts
- Checkout and receipt generation
- Sales history
- Revenue dashboard at `/`
- Swagger/OpenAPI at `/docs`
- Automated API tests
- Docker-ready deployment

## Stack
Python · FastAPI · Pydantic · SQLite/PostgreSQL-ready architecture · Docker

## Run locally
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn api:app --reload
```
Open `http://127.0.0.1:8000/`.

## Core API
`POST /products`, `GET /products`, `DELETE /products/{sku}`, `POST /checkout`, `GET /sales`, and `GET /dashboard`.

> Demo POS backend. Use a persistent transactional database, authentication, audit logs, tax rules, and payment-provider integration before production deployment.
