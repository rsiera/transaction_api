# Transaction API - Transaction Data Processing and Aggregation System

Backend system for importing, validating, processing and aggregating transaction data from various systems.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)

## 🎯 Overview

Transaction API is a backend tool that enables:
- Import transaction data from CSV files
- Data validation and processing
- Storage in relational database (sqlite3)
- Data access and aggregated reports via REST API

## ✨ Features

### 1. Data Import
- **Endpoint**: `POST /api/v1.0/transactions/upload/`
- CSV file upload with transaction data
- Asynchronous processing with Celery
- Data validation (UUID, ISO 8601 dates, numeric types)
- Automatic currency conversion to PLN
- Error logging without blocking valid data

### 2. Data Retrieval
- **Transaction list**: `GET /api/v1.0/transactions/`
  - Pagination
  - Filtering by `customer_id` and `product_id`
- **Transaction details**: `GET /api/v1.0/transactions/{transaction_id}/`

### 3. Aggregation Reports
- **Customer summary**: `GET /api/v1.0/transactions/reports/customer-summary/{customer_id}/`
  - Total amount spent (PLN)
  - Number of unique products
  - Last transaction date
  
- **Product summary**: `GET /api/v1.0/transactions/reports/product-summary/{product_id}/`
  - Total quantity sold
  - Total revenue (PLN)
  - Number of unique customers

## 📦 Requirements

- Python 3.11.13
- Sqlite 
- Redis (for Celery)

### CSV File Format

```csv
transaction_id,timestamp,amount,currency,customer_id,product_id,quantity
550e8400-e29b-41d4-a716-446655440000,2025-01-15T10:30:00Z,100.50,PLN,660e8400-e29b-41d4-a716-446655440001,770e8400-e29b-41d4-a716-446655440002,2
```

## Installation

1. **Install dependencies:**
   ```bash
   python3 -m venv venv
   source bin/activate
   pip install -r requirement/base.txt
   ```
2. **Run the Django REST API server and admin app:**
   ```bash
   python manage.py runserver
   ```