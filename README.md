# Inventory & POS System

Professional inventory and point-of-sale backend for small and medium businesses.

## Features
- Product catalog and SKU management
- Stock in/out and low-stock alerts
- Cart and checkout workflow
- Sales totals and daily dashboard metrics
- Transaction-safe service design
- REST API and Swagger docs

## Stack
Python · FastAPI · Pydantic · SQLite/PostgreSQL-ready · Docker

## Quick start
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn api:app --reload
```
Open `http://127.0.0.1:8000/docs`.
