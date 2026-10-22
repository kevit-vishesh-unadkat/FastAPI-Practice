# from resource import RLIMIT_AS
#
# from fastapi import FastAPI,Query
#
# app=FastAPI()
#
# # sample data
# products=[
#     {"id": i, "name": f"Product {i}", "price": i * 100}
#     for i in range(1, 101)
# ]
#
# @app.get("/")
# def home():
#     return {
#         "message":"Hello From Vishesh"
#     }
#
# @app.get("/products")
# def get_product(
#         page:int=Query(default=1,ge=1),
#         limit:int=Query(default:10,ge=1,le=100)
# ):
#
#     start=(page-1)*limit
#


from fastapi import FastAPI, Query

app = FastAPI()

# Sample data
products = [
    {"id": i, "name": f"Product {i}", "price": i * 100}
    for i in range(1, 101)
]


@app.get("/")
def home():
    return {"message": "FastAPI Pagination API"}


@app.get("/products")
def get_products(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=50)
):
    # Calculate the starting index
    start = (page - 1) * limit

    # Calculate the ending index
    end = start + limit

    # Get products for the requested page
    paginated_products = products[start:end]

    return {
        "page": page,
        "limit": limit,
        "total_products": len(products),
        "total_pages": (len(products) + limit - 1) // limit,
        "products": paginated_products
    }



