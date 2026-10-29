# Inventory Service - Step 2

This is the Inventory Service in the Flask microservices learning project.

## Responsibility
- Categories
- Products
- Stock movements

## Architecture
HTTP Request -> Controller -> Service -> Repository -> Model -> Database

## Run
1. Create/activate your virtual environment.
2. Install dependencies used by the original project.
3. Configure the MySQL database in `config/db_config.py`.
4. Run:

```bash
python app.py
```

The service keeps the original API routes and business logic from the inventory project.

## Current service boundary
- Inventory Service: categories, products, stock movements
- User Service: authentication and users (Step 1)

At this step the services are independent. Service-to-service communication, API Gateway, RabbitMQ, Docker Compose and Kubernetes will be introduced in later steps.
