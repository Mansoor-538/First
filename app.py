from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

app = FastAPI(title="Minimal E-Commerce API")

# ==========================================
# 1. SCHEMAS & MODELS (Data Validation)
# ==========================================
class Product(BaseModel):
    id: int
    name: str
    price: float = Field(gt=0, description="Price must be greater than zero")
    category: str
    stock: int = Field(ge=0, description="Stock cannot be negative")


class CartItem(BaseModel):
    product_id: int
    quantity: int = Field(gt=0, description="Quantity must be at least 1")


class OrderSummary(BaseModel):
    items: List[Dict]
    subtotal: float
    tax: float
    total: float


# ==========================================
# 2. IN-MEMORY DATABASE (Mock Data)
# ==========================================
products_db: Dict[int, Product] = {
    1: Product(id=1, name="Wireless Mouse", price=25.99, category="Electronics", stock=15),
    2: Product(id=2, name="Mechanical Keyboard", price=89.99, category="Electronics", stock=8),
    3: Product(id=3, name="Coffee Mug", price=12.50, category="Kitchen", stock=50),
}

# Mock active cart tracking { user_id: { product_id: quantity } }
carts_db: Dict[int, Dict[int, int]] = {}

TAX_RATE = 0.08  # 8% sales tax


# ==========================================
# 3. API ENDPOINTS
# ==========================================

# --- Product Catalog Routes ---
@app.get("/products", response_model=List[Product])
def get_products():
    """Retrieve all available products."""
    return list(products_db.values())


@app.get("/products/{product_id}", response_model=Product)
def get_product(product_id: int):
    """Retrieve details for a single product."""
    if product_id not in products_db:
        raise HTTPException(status_code=404, detail="Product not found")
    return products_db[product_id]


# --- Cart Routing ---
@app.post("/cart/{user_id}/add", status_code=status.HTTP_200_OK)
def add_to_cart(user_id: int, item: CartItem):
    """Add an item to the user's shopping cart."""
    # Check if product exists
    if item.product_id not in products_db:
        raise HTTPException(status_code=404, detail="Product not found")

    product = products_db[item.product_id]

    # Check stock availability
    if product.stock < item.quantity:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient stock. Only {product.stock} items left.",
        )

    # Initialize cart if user is new
    if user_id not in carts_db:
        carts_db[user_id] = {}

    # Update or add quantity
    current_qty = carts_db[user_id].get(item.product_id, 0)
    if product.stock < (current_qty + item.quantity):
        raise HTTPException(status_code=400, detail="Cannot exceed available stock")

    carts_db[user_id][item.product_id] = current_qty + item.quantity
    return {"message": f"Added {item.quantity} x {product.name} to cart"}


# --- Checkout & Order Summary ---
@app.get("/cart/{user_id}/checkout", response_model=OrderSummary)
def checkout(user_id: int):
    """Calculate subtotal, tax, and order total for checkout."""
    user_cart = carts_db.get(user_id)
    if not user_cart or len(user_cart) == 0:
        raise HTTPException(status_code=400, detail="Your shopping cart is empty")

    subtotal = 0.0
    items_summary = []

    # Calculate individual line items and subtotal
    for prod_id, qty in user_cart.items():
        product = products_db[prod_id]
        item_total = product.price * qty
        subtotal += item_total

        items_summary.append(
            {
                "product_id": prod_id,
                "name": product.name,
                "unit_price": product.price,
                "quantity": qty,
                "item_total": round(item_total, 2),
            }
        )

    # Apply global calculations
    tax = subtotal * TAX_RATE
    total = subtotal + tax

    return OrderSummary(
        items=items_summary,
        subtotal=round(subtotal, 2),
        tax=round(tax, 2),
        total=round(total, 2),
    )
