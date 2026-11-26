from fastapi import FastAPI

# 1. Instanciamos la aplicación definiendo los metadatos del contrato OpenAPI (en inglés técnico)
app = FastAPI(
    title="Store RESTful API",
    description="Backend API service for product catalog, inventory management and JWT authentication.",
    version="1.0.0",
)

# Catálogo inicial en memoria (en los próximos capítulos conectaremos SQLite con SQLAlchemy)
SAMPLE_PRODUCTS = [
    {"id": 1, "name": "Mechanical RGB Keyboard", "price": 49.99, "is_available": True},
    {"id": 2, "name": "Wireless Gaming Mouse", "price": 29.99, "is_available": True},
    {"id": 3, "name": "27-inch 4K Monitor", "price": 299.99, "is_available": False},
]


# 2. Endpoint de verificación de estado del servidor (Healthcheck)
@app.get("/", tags=["Healthcheck"])
async def root() -> dict[str, str]:
    """Verify that the API service is online and operational."""
    return {
        "status": "online",
        "message": "Welcome to the Store RESTful API",
        "docs_url": "/docs",
    }


# 3. READ (Colección): Obtener la lista completa de productos
@app.get("/products", tags=["Products"])
async def get_products() -> list[dict[str, int | str | float | bool]]:
    """Retrieve the complete list of products in the catalog."""
    return SAMPLE_PRODUCTS


@app.get("/store-info", tags=["Store"])
async def get_store_info() -> dict[str, str | int]:
    """info about the store"""
    return {
        "store_name": "Canarias Tech Store Api",
        "version": "1.0.0",
        "currency": "EUR",
        "total_products": len(SAMPLE_PRODUCTS),
    }


@app.get("/products/avaible", tags=["Products"])
async def get_avaible_products() -> list[dict[str, int | str | float | bool]]:
    """ "Info about the avaible items"""
    return [prod for prod in SAMPLE_PRODUCTS if prod["is_available"]]
