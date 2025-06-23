# Product API

This repository contains the backend setup for an **E-commerce Product API**, built using **FastAPI**, **SQLAlchemy**, and **MySQL**. The goal is to create a real-time, scalable product management system, complete with category hierarchies, inventory updates, and dynamic pricing.

---
## Day09 - 17/06/2025 - Day 1 of Product API

### 1. Database Models Design
- Designed relational models for:
  - **Products**: Includes name, price, stock, brand, attributes, etc.
  - **Categories**: Supports parent-child category relationships.
  - **Price History**: Logs price changes for audit and analytics.

### 2. Pydantic Schemas
- Created schema classes to validate and serialize API data.
- Incorporated nested relationships like `Product` → `Category` and `PriceHistory`.
- Enabled forward references and automatic ORM data conversion.

### 3. Core CRUD Operations
- Built essential database operations using SQLAlchemy ORM:
  - Create new product entries.
  - Retrieve products (all, by ID, by category, or via search).
  - Fetch all category entries.

### 4. Data Generation Utilities
- Created a **data generator class** using the **Faker** library:
  - Auto-generates product and category data with realistic values.
  - Simulates dynamic price and stock updates.
  - Creates hierarchical global category structures with subcategories.
  - Supports real-time new product generation and historical pricing logs.

### 5. Environment and Database Setup
- Connected the app to a **MySQL database** using SQLAlchemy.
- Secured sensitive DB credentials using environment variables (`.env` file).
- Set up database session handling for dependency injection.

---

## Next Steps (Planned)
- Implement full API endpoints using FastAPI.
- Add pagination, filtering, and sorting to the product listing endpoint.
- Integrate background tasks for real-time stock and price updates.

---

## Tech Stack
- **Backend**: FastAPI
- **ORM**: SQLAlchemy
- **Database**: MySQL
- **Data Generation**: Faker as Mimesis has deprecated lots of built in providers
- **Environment Management**: dotenv


## Day10 - 18/06/2025 - Day 2 of Product API

Building upon yesterday's foundation, today focused on implementing the complete API layer with advanced features including background automation, comprehensive pagination, and real-time data updates.

### 1. FastAPI Router Implementation
- **Product Router**: Created comprehensive API endpoints with proper REST conventions:
  - `POST /products/` - Create new products manually
  - `GET /products/` - Advanced product listing with pagination, filtering, and sorting
  - `GET /products/{product_id}` - Retrieve individual product details
  - `POST /products/auto-generate` - Bulk product generation endpoint
  - `POST /products/update-prices` - Manual price update trigger
  - `POST /products/update-stock` - Manual stock update trigger

### 2. Advanced Pagination & Filtering System
- **Smart Pagination**: Implemented clean pagination with metadata (total pages, current page, per_page)
- **Multi-Parameter Filtering**: 
  - Price range filtering (`min_price`, `max_price`)
  - Category-based filtering (`category_id`)
  - Stock availability filtering (`in_stock_only`)
  - Text search across product names and brands
- **Dynamic Sorting**: Configurable sorting by any product field with ascending/descending options
- **Clean Response Structure**: Optimized API responses with essential product information and ratings

### 3. Background Job Automation System
- **APScheduler Integration**: Implemented background scheduler for automated tasks
- **Three Automated Jobs**:
  - **Product Generation**: Auto-creates 10-100 new products every 30 seconds
  - **Price Updates**: Randomly updates product prices every 60 seconds with history logging
  - **Stock Updates**: Simulates inventory changes every 90 seconds
- **Environment-Controlled**: Scheduler can be enabled/disabled via `ENABLE_SCHEDULER` environment variable
- **Error Handling**: Robust exception handling for all scheduled tasks


### 5. Enhanced CRUD Operations
- **Advanced Query Building**: Complex SQLAlchemy queries with multiple filters and joins
- **Optimized Database Access**: Used `joinedload` for efficient category relationship loading
- **Pagination Logic**: Database-level pagination with total count calculation
- **Search Functionality**: Case-insensitive text search across multiple fields

### 6. Logging
- Included Logging for every possible python file by replacing it with print statements

---

## API Endpoints Overview

| Method | Endpoint                  | Description       | Key Features                            |
|--------|---------------------------|-------------------|-----------------------------------------|
| `GET`  | `/`                       | Root endpoint     | Basic API status                        |
| `GET`  | `/health`                 | Health check      | Scheduler status monitoring             |
| `POST` | `/products/`              | Create product    | Manual product creation                 |
| `GET`  | `/products/`              | List products     | Pagination, filtering, sorting, search  |
| `GET`  | `/products/{id}`          | Get product       | Full product details with relationships |
| `POST` | `/products/auto-generate` | Generate products | Bulk automated product creation         |
| `POST` | `/products/update-prices` | Update prices     | Manual price update trigger             |
| `POST` | `/products/update-stock`  | Update stock      | Manual inventory update trigger         |
---

## Key Technical Achievements

### Advanced Query Parameters
- **Pagination**: `page`, `per_page` with intelligent defaults
- **Search**: Cross-field text search with case-insensitive matching  
- **Sorting**: `sort_by`, `sort_dir` with field validation
- **Filtering**: Price ranges, categories, stock availability

### Background Automation
- **Real-time Updates**: Continuous price and stock fluctuations
- **Scalable Generation**: Automatic product catalog expansion
- **Configurable Scheduling**: Environment-based scheduler control

---

## Next Steps (Planned)
- Create WebSocket connections for real-time price updates
- Implement caching layer for improved performance
- Add comprehensive API documentation with OpenAPI/Swagger enhancements

---

## Tech Stack
- **Backend**: FastAPI
- **Background Jobs**: APScheduler
- **Environment Management**: dotenv
- **API Documentation**: OpenAPI/Swagger (auto-generated)

---

## Environment Variables
```env
ENABLE_SCHEDULER=true  # Set to 'false' to disable background jobs
```
