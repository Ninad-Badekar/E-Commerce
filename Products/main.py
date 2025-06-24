import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from apscheduler.schedulers.background import BackgroundScheduler
from Products.database import engine, Base, SessionLocal
from Products.crud import get_all_products
from Products.routers import product_router
from Products.data_generator import DataGenerator
import os
from dotenv import load_dotenv
from Products.logger import log
import random
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

load_dotenv()

scheduler = BackgroundScheduler()
generator = DataGenerator()

def scheduled_generate_product():
    db = SessionLocal()
    try:
        categories = generator.get_categories(db)
        if categories:
            count = random.randint(10,60)
            log.info(f"Generating {count} new products...")
            generator.create_products(db, categories, count=count)
    except Exception as e:
        log.error(f"Error in scheduled_generate_product: {e}")
    finally:
        db.close()

def scheduled_price_update():
    db = SessionLocal()
    try:
        products = get_all_products(db)
        if products:
            log.info("Updating product prices...")
            generator.randomly_update_prices(db, products)
    except Exception as e:
        log.error(f"Error in scheduled_price_update: {e}")
    finally:
        db.close()

def scheduled_stock_update():
    db = SessionLocal()
    try:
        products = get_all_products(db)
        if products:
            log.info("Updating product stock quantities...")
            generator.randomly_update_stocks(db, products)
    except Exception as e:
        log.error(f"Error in scheduled_stock_update: {e}")
    finally:
        db.close()

print("Tables found:", Base.metadata.tables.keys())

ENABLE_SCHEDULER = os.getenv("ENABLE_SCHEDULER", "false").lower() == "true"

@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("Starting up...")
    
    try:
        Base.metadata.create_all(bind=engine)
        log.info("Database tables created or already exist.")
    except Exception as e:
        log.error(f"Error creating tables: {e}")

    db = SessionLocal()
    try:
        categories = generator.get_categories(db)
        if not categories:
            log.info("No categories found, creating initial categories...")
            generator.create_categories(db)
        else:
            log.info(f"Found {len(categories)} existing categories.")
    except Exception as e:
        log.error(f"Error initializing categories: {e}")
    finally:
        db.close()

    if ENABLE_SCHEDULER:
        log.info("Scheduler is enabled.")
        scheduler.add_job(scheduled_generate_product, "interval", seconds=30, id="generate_product")
        scheduler.add_job(scheduled_price_update, "interval", seconds=600, id="price_update")
        scheduler.add_job(scheduled_stock_update, "interval", seconds=900, id="stock_update")
        scheduler.start()
        log.info("Scheduler jobs started.")
    else:
        log.warning("Scheduler disabled — products will only generate manually")

    try:
        yield
    except asyncio.CancelledError:
        log.warning("Lifespan cancelled (probably due to shutdown)")
        raise
    finally:
        log.info("Shutting down...")
        if ENABLE_SCHEDULER and scheduler.running:
            scheduler.shutdown(wait=False)
            log.info("Scheduler shutdown complete.")


app = FastAPI(
    title="E-commerce Product API", 
    version="1.0",
    lifespan=lifespan
)

app.include_router(product_router.router)

@app.get("/")
def root():
    log.info("Root endpoint accessed.")
    return {"message": "Product API is running"}

@app.get("/health")
def health_check():
    log.info("Health check endpoint accessed.")
    return {
        "status": "healthy",
        "scheduler_running": scheduler.running,
        "jobs": [job.id for job in scheduler.get_jobs()]
    }
