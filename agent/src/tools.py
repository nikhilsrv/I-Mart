"""
LangGraph tools for I-Mart voice agent.
These tools allow the agent to interact with the e-commerce backend.
"""

import aiohttp
from langchain_core.tools import tool

from src.config import settings


async def _api_request(method: str, endpoint: str, data: dict | None = None) -> dict:
    """Make request to I-Mart API."""
    url = f"{settings.IMART_API_URL}{endpoint}"
    async with aiohttp.ClientSession() as session:
        async with session.request(method, url, json=data) as response:
            if response.status == 200:
                return await response.json()
            return {"error": f"API error: {response.status}"}


@tool
async def search_products(query: str, category: str | None = None) -> str:
    """
    Search for products in the I-Mart catalog.

    Args:
        query: Search term (e.g., "wireless headphones", "laptop")
        category: Optional category filter (e.g., "electronics", "clothing")

    Returns:
        List of matching products with name, price, and availability.
    """
    params = {"q": query}
    if category:
        params["category"] = category

    result = await _api_request("GET", f"/api/products/search?q={query}")

    if "error" in result:
        return f"Sorry, I couldn't search for products right now. {result['error']}"

    if not result.get("products"):
        return f"No products found for '{query}'. Try a different search term."

    products = result["products"][:5]  # Limit to 5 results for voice
    response = f"I found {len(products)} products:\n"
    for p in products:
        response += f"- {p['name']}: ₹{p['price']} ({p.get('stock', 'In stock')})\n"

    return response


@tool
async def get_product_details(product_id: str) -> str:
    """
    Get detailed information about a specific product.

    Args:
        product_id: The unique identifier of the product.

    Returns:
        Product details including description, price, specifications.
    """
    result = await _api_request("GET", f"/api/products/{product_id}")

    if "error" in result:
        return "Sorry, I couldn't find that product."

    p = result
    return (
        f"{p['name']}\n"
        f"Price: ₹{p['price']}\n"
        f"Description: {p.get('description', 'No description')}\n"
        f"In Stock: {p.get('stock', 'Unknown')}"
    )


@tool
async def add_to_cart(product_id: str, quantity: int = 1) -> str:
    """
    Add a product to the user's shopping cart.

    Args:
        product_id: The unique identifier of the product to add.
        quantity: Number of items to add (default: 1).

    Returns:
        Confirmation message or error.
    """
    result = await _api_request(
        "POST",
        "/api/cart/items",
        {"product_id": product_id, "quantity": quantity},
    )

    if "error" in result:
        return "Sorry, I couldn't add that to your cart. Please try again."

    return f"Added {quantity} item(s) to your cart. Would you like to continue shopping or checkout?"


@tool
async def get_cart() -> str:
    """
    Get the current contents of the user's shopping cart.

    Returns:
        List of items in cart with quantities and total price.
    """
    result = await _api_request("GET", "/api/cart")

    if "error" in result:
        return "Sorry, I couldn't retrieve your cart right now."

    items = result.get("items", [])
    if not items:
        return "Your cart is empty. Would you like to search for products?"

    response = "Your cart contains:\n"
    total = 0
    for item in items:
        subtotal = item["price"] * item["quantity"]
        total += subtotal
        response += f"- {item['name']} x{item['quantity']}: ₹{subtotal}\n"

    response += f"\nTotal: ₹{total}"
    return response


@tool
async def get_order_status(order_id: str) -> str:
    """
    Check the status of an existing order.

    Args:
        order_id: The unique identifier of the order.

    Returns:
        Order status and details.
    """
    result = await _api_request("GET", f"/api/orders/{order_id}")

    if "error" in result:
        return f"Sorry, I couldn't find order {order_id}. Please check the order ID."

    return (
        f"Order {order_id}:\n"
        f"Status: {result['status']}\n"
        f"Items: {len(result.get('items', []))} item(s)\n"
        f"Total: ₹{result.get('total', 'N/A')}\n"
        f"Expected delivery: {result.get('delivery_date', 'Not available')}"
    )


@tool
async def get_categories() -> str:
    """
    Get list of available product categories.

    Returns:
        List of product categories.
    """
    result = await _api_request("GET", "/api/categories")

    if "error" in result:
        return "Sorry, I couldn't fetch categories right now."

    categories = result.get("categories", [])
    if not categories:
        return "No categories available."

    return "Available categories: " + ", ".join(c["name"] for c in categories)


# All tools available to the agent
ALL_TOOLS = [
    search_products,
    get_product_details,
    add_to_cart,
    get_cart,
    get_order_status,
    get_categories,
]
