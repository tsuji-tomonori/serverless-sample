from dyntastic import A
from dyntastic.exceptions import DoesNotExist
from fastapi import FastAPI
from fastapi import HTTPException
from fastapi import Response

from api.models import Product
from api.models import ProductResponse
from api.models import ProductUpdate

app = FastAPI()


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.post("/products/")
def create_product(product: Product) -> ProductResponse:
    try:
        # 既存レコードがあれば何もせず existing に格納
        existing = Product.get(product.product_id, consistent_read=True)
    except DoesNotExist:
        # レコード未存在時は existing = None のまま
        existing = None

    if existing:
        # 重複時は 409 Conflict
        raise HTTPException(status_code=409, detail="Product already exists")
    # 新しい商品を作成
    product.save()
    return product  # type: ignore


@app.get("/products/")
def list_products() -> list[ProductResponse]:
    # DynamoDB の Scan API を使用して全アイテムを取得
    items = Product.scan()
    return list(items)  # type: ignore


@app.get("/products/{product_id}")
def read_product(product_id: str) -> ProductResponse:
    try:
        product = Product.get(product_id)
    except DoesNotExist as e:
        raise HTTPException(status_code=404, detail="Product not found") from e
    return product  # type: ignore


@app.patch("/products/{product_id}")
def update_product(product_id: str, product: ProductUpdate) -> ProductResponse:
    try:
        item = Product.get(product_id)
    except DoesNotExist as e:
        raise HTTPException(status_code=404, detail="Product not found") from e

    # 部分更新: リクエスト JSON のキー/値を属性更新式に変換
    expressions = []
    # 明示的に設定されたフィールドのみ取得
    update_data = product.model_dump(exclude_unset=True)

    if "name" in update_data:
        expressions.append(A("name").set(update_data["name"]))
    if "description" in update_data:
        expressions.append(A("description").set(update_data["description"]))
    if "price" in update_data:
        expressions.append(A("price").set(update_data["price"]))

    # フィールドが指定されていなければエラー
    if not expressions:
        raise HTTPException(status_code=400, detail="No fields to update")

    # 更新式を適用
    item.update(*expressions)
    return Product.get(product_id)  # type: ignore


@app.delete("/products/{product_id}", status_code=204)
def delete_product(product_id: str) -> Response:
    try:
        item = Product.get(product_id)
    except DoesNotExist as e:
        raise HTTPException(status_code=404, detail="Product not found") from e
    item.delete()
    return Response(status_code=204)


@app.delete("/test/clear-table", status_code=204)
def clear_table() -> Response:
    """テスト用: テーブル内の全アイテムを削除"""
    items = Product.scan()
    for item in items:
        item.delete()
    return Response(status_code=204)
