import os
import uuid
from datetime import datetime
from datetime import timezone
from decimal import Decimal

from dyntastic import Dyntastic
from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field
from pydantic import field_serializer


class Product(Dyntastic):
    __table_name__ = os.getenv("DYNAMODB_PRODUCT_TABLE_NAME", "products")
    __hash_key__ = "product_id"
    __table_host__ = os.getenv("DYNAMODB_ENDPOINT_URL", "http://dynamodb-local:8000")

    # Pydantic v2 設定
    model_config = ConfigDict(
        populate_by_name=True,
    )

    product_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str | None = None
    price: Decimal
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_serializer("price", mode="plain")
    def serialize_price(self, v: Decimal) -> str:
        # Decimal を文字列に変換
        return str(v)

    @field_serializer("created_at", mode="plain")
    def serialize_created_at(self, v: datetime) -> str:
        # ISOフォーマット文字列に変換
        return v.isoformat()


class ProductUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    price: Decimal | None = None


class ProductResponse(BaseModel):
    product_id: str
    name: str
    description: str | None = None
    price: Decimal
    created_at: datetime
