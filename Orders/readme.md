# E-commerce Orders API

This project implemented a simple Orders microservice using FastAPI, SQLAlchemy and Pydantic. It provided endpoints to create, list, retrieve and update order statuses, complete with database configuration, dependency management, error-handling middleware, custom exception handlers and a standalone data seeder.


## Implementation Summary

### 1. db.py  
- Loaded `DATABASE_URL` from environment variables.  
- Defined `SessionLocal` as a `sessionmaker` bound to the engine.

### 2. dependencies.py  
- Implemented `get_db()` as a FastAPI dependency that opened a database session and closed it after each request.

### 3. models.py  
- Declared `Base = declarative_base()`.  
- Defined an `OrderStatus` enum (`pending`, `shipped`, `delivered`).  
- Created an `Order` SQLAlchemy model with columns:  
  - `order_id` (UUID string primary key)  
  - `customer_id` (UUID string)  
  - `order_date` (auto-generated timestamp)  
  - `items` (JSON column)  
  - `total_amount` (float)  
  - `status` (enum)  
  - `payment_method` (string)  
  - `shipping_address` (string)

### 4. schemas.py  
- Introduced Pydantic models for request/response validation:  
  - `Item` (fields: `product_id: UUID`, `name`, `quantity`, `price`)  
  - `OrderCreate` (fields: `customer_id: UUID`, `items: List[Item]`, `payment_method`, `shipping_address`)  
  - `OrderResponse` (fields: `order_id`, `order_date`, `total_amount`, `status`)

### 5. crud.py  
- Built four core functions against the database session:  
  1. `create_order()`  
     - Computed `total_amount`.  
     - Converted all UUIDs to strings for JSON serialization.  
     - Inserted and returned a new `Order`.  
  2. `get_order()`  
     - Queried by `order_id` and raised HTTP 404 on miss.  
  3. `list_orders()`  
     - Returned all orders.  
  4. `update_order_status()`  
     - Validated the new status against `OrderStatus` and raised HTTP 400 on invalid values.  
     - Committed and returned the updated record.

### 6. middleware.py  
- Added an HTTP middleware `log_errors` that caught unhandled exceptions, logged the stack trace, and returned a 500 JSON response.

### 7. exceptions.py  
- Provided `custom_exception_handler` to render FastAPI’s `HTTPException` and other exceptions as consistent JSON payloads.

### 8. main.py  
- Instantiated the `FastAPI` app with CORS enabled for all origins.  
- Mounted the `log_errors` middleware and the `custom_exception_handler`.  
- Created database tables on startup via `Base.metadata.create_all(bind=engine)`.  
- Defined the following endpoints under `/orders`:  
  - `POST /orders/` to create either a manually supplied order or 1–5 fake orders with Faker.  
  - `GET  /orders/` to list all orders.  
  - `GET  /orders/{order_id}` to retrieve a single order.  
  - `PUT  /orders/{order_id}/status` to update an order’s status.

### 9. seed_data.py  
- Ensured the `orders` table existed by calling `Base.metadata.create_all(bind=engine)`.  
- Generated 500 fake orders using Faker; guaranteed `Item.name` satisfied the `min_length=2` constraint.  
- Coerced raw dicts into Pydantic `Item` and `OrderCreate` objects, then persisted them via `create_order()`.

### 10. Run the application
- uvicorn main:app --reload