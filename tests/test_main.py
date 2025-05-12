import boto3
import pytest
from fastapi.testclient import TestClient
from moto import mock_aws

from api.main import app


@pytest.fixture
def client():
    with mock_aws():
        # テーブル作成
        dynamodb = boto3.resource("dynamodb")
        dynamodb.create_table(
            TableName="products",
            KeySchema=[{"AttributeName": "product_id", "KeyType": "HASH"}],
            AttributeDefinitions=[
                {"AttributeName": "product_id", "AttributeType": "S"}
            ],
            BillingMode="PAY_PER_REQUEST",
        )
        # モデルにモックテーブルを差し替え
        yield TestClient(app)


# テストデータ
PRODUCT_1 = {"product_id": "p1", "name": "Prod1", "description": "Desc1", "price": 10}
PRODUCT_2 = {"product_id": "p2", "name": "Prod2", "description": "Desc2", "price": 20}


# 正常系: 作成、取得、一覧、更新、削除
def test_create_and_read_and_list_and_delete_product(client: TestClient):
    # 作成
    resp_create = client.post("/products/", json=PRODUCT_1)
    assert resp_create.status_code == 200
    data1 = resp_create.json()
    assert "created_at" in data1
    data1.pop("created_at")
    assert data1 == PRODUCT_1

    # 重複作成エラー
    resp_conflict = client.post("/products/", json=PRODUCT_1)
    assert resp_conflict.status_code == 409

    # 単一取得
    resp_read = client.get(f"/products/{PRODUCT_1['product_id']}")
    assert resp_read.status_code == 200
    data2 = resp_create.json()
    assert "created_at" in data2
    data2.pop("created_at")
    assert data2 == PRODUCT_1

    # 存在しない取得エラー
    resp_notfound = client.get("/products/nonexistent")
    assert resp_notfound.status_code == 404

    # 一覧 (現在 1 件)
    resp_list = client.get("/products/")
    assert resp_list.status_code == 200
    data3 = resp_list.json()
    assert isinstance(data3, list)
    assert len(data3) == 1
    assert "created_at" in data3[0]
    data3[0].pop("created_at")
    assert data3[0] == PRODUCT_1

    # 更新: name のみ
    patch_data = {"name": "UpdatedName"}
    resp_patch = client.patch(f"/products/{PRODUCT_1['product_id']}", json=patch_data)
    assert resp_patch.status_code == 200
    updated = resp_patch.json()
    assert updated["name"] == "UpdatedName"
    # 他フィールドは不変
    assert updated["description"] == PRODUCT_1["description"]
    assert updated["price"] == PRODUCT_1["price"]

    # 更新: フィールド指定なしエラー
    resp_patch_empty = client.patch(f"/products/{PRODUCT_1['product_id']}", json={})
    assert resp_patch_empty.status_code == 400

    # 更新: 存在しない商品エラー
    resp_patch_nf = client.patch("/products/nonexistent", json={"name": "X"})
    assert resp_patch_nf.status_code == 404

    # 削除
    resp_delete = client.delete(f"/products/{PRODUCT_1['product_id']}")
    assert resp_delete.status_code == 204
    # 削除後は取得 404
    resp_read_after = client.get(f"/products/{PRODUCT_1['product_id']}")
    assert resp_read_after.status_code == 404

    # 存在しない削除エラー
    resp_delete_nf = client.delete("/products/doesnotexist")
    assert resp_delete_nf.status_code == 404


# 正常系: 複数アイテムの一覧
def test_list_multiple_products(client: TestClient):
    client.post("/products/", json=PRODUCT_1)
    client.post("/products/", json=PRODUCT_2)
    resp = client.get("/products/")
    assert resp.status_code == 200
    data = resp.json()
    # 2 件が含まれる
    ids = {item["product_id"] for item in data}
    assert ids == {"p1", "p2"}


# 異常系: 部分更新の異常カバレッジを追加
def test_partial_update_multiple_fields(client: TestClient):
    client.post("/products/", json=PRODUCT_2)
    patch_data = {"description": "NewDesc", "price": 99}
    resp = client.patch(f"/products/{PRODUCT_2['product_id']}", json=patch_data)
    assert resp.status_code == 200
    updated = resp.json()
    assert updated["description"] == "NewDesc"
    assert updated["price"] == 99
    # name は元のまま
    assert updated["name"] == PRODUCT_2["name"]
