# simple paggination with crud operation

from fastapi import FastAPI ,HTTPException ,Query
from pydantic import BaseModel,Field

app=FastAPI()

class Product(BaseModel):
    name:str=Field(min_length=2)
    price:float=Field(gt=0)
    quantity:int=Field(gt=0)

# in memory storage
products=[]
next_id=1

@app.post("/products",status_code=201)
def create_product(product:Product):
    global next_id

    new_product={
        "id":next_id,
        **product.model_dump()
    }

    products.append(new_product)
    next_id+=1

    return {
        "message":"product created successfully",
        "product":new_product
    }


# get product by id

@app.get("/products/{product_id}")
def get_product_by_id(product_id:int):

    for product in products:
        if product["id"]==product_id:
            return product
    raise HTTPException(
        status_code=404,
        detail="product not found"
    )


# get all product

@app.get("/products")
def get_products(
        page:int = Query(default=1,ge=1),
        limit:int=Query(default=5,gt=1,le=50)
):
    total_product=len(products)

    start=(page-1)*limit
    end=start+limit

    paginated_products = products[start:end]

    total_pages = (total_product + limit - 1) // limit

    return {
        "page": page,
        "limit": limit,
        "total_products": total_product,
        "total_pages": total_pages,
        "products": paginated_products
    }