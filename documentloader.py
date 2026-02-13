from data import data
from langchain_core.documents import Document



def product_to_text(product):
    tags = ", ".join(product.get("tags", []))
    metadata = ". ".join(f"{k}: {v}" for k, v in product.get("metadata", {}).items())
    return (
        f"{product['name']} ({product['id']}). "
        f"{product['description']} "
        f"Category: {product['category']}. "
        f"Price: ${product['price']} {product['currency']}. "
        f"Vendor: {product['vendor']}. "
        f"Status: {product['status']}. "
        f"Tags: {tags}. "
        f"{metadata}"
    )


documents = [
    Document(
        page_content=product_to_text(p),
        metadata={"id": p["id"], "category": p["category"], "vendor": p["vendor"], "status": p["status"]},
    )
    for p in data
]
