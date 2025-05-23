from behave import given  # type: ignore[reportMissingTypeStubs]
from behave import then  # type: ignore[reportMissingTypeStubs]
from behave import when  # type: ignore[reportMissingTypeStubs]
from fastapi.testclient import TestClient

from api.main import app

# テスト用固定データ
PRODUCT_FIXTURES = {
    "p1": {"product_id": "p1", "name": "Prod1", "description": "Desc1", "price": 10},
    "p2": {"product_id": "p2", "name": "Prod2", "description": "Desc2", "price": 20},
}


@given("製品テーブルが空である")
def step_empty_table(context):
    # 新しい TestClient を作成し、異なるテスト間でクリーンな状態を維持
    context.client = TestClient(app)
    # テーブルをクリア
    context.client.delete("/test/clear-table")


@given('product_id "{product_id}" の製品が存在するとき')
def step_product_exists(context, product_id):
    # 固定データで製品を作成
    data = PRODUCT_FIXTURES.get(product_id)
    assert data, f"Fixture not found for {product_id}"
    resp = context.client.post("/products/", json=data)
    assert resp.status_code == 200
    context.response = resp


@given("以下の製品が存在するとき")
def step_multiple_products_exist(context):
    for row in context.table:
        item = {
            "product_id": row["product_id"],
            "name": row["name"],
            "description": row.get("description"),
            "price": int(row["price"]),
        }
        resp = context.client.post("/products/", json=item)
        assert resp.status_code == 200
    context.response = resp


@when('POSTリクエストを "{endpoint}" に以下のJSONで送信するとき')
def step_post_json(context, endpoint):
    payload = {
        row[0]: (int(row[1]) if row[0] == "price" else row[1]) for row in context.table
    }
    context.response = context.client.post(endpoint, json=payload)


@when('GETリクエストを "{endpoint}" に送信するとき')
def step_get(context, endpoint):
    context.response = context.client.get(endpoint)


@when('PATCHリクエストを "{endpoint}" に空のJSONで送信するとき')
def step_patch_empty(context, endpoint):
    context.response = context.client.patch(endpoint, json={})


@when('PATCHリクエストを "{endpoint}" に以下のJSONで送信するとき')
def step_patch_json(context, endpoint):
    payload = {
        row[0]: (int(row[1]) if row[0] == "price" else row[1]) for row in context.table
    }
    context.response = context.client.patch(endpoint, json=payload)


@when('DELETEリクエストを "{endpoint}" に送信するとき')
def step_delete(context, endpoint):
    context.response = context.client.delete(endpoint)


@then("レスポンスのステータスコードは{status_code:d}である")
def step_status_code(context, status_code):
    assert context.response.status_code == status_code


@then('レスポンスJSONにフィールド "{field}" が含まれている')
def step_json_field(context, field):
    data = context.response.json()
    assert field in data


@then("レスポンスJSONは次と一致する")
def step_json_matches(context):
    expected = {
        row[0]: (int(row[1]) if row[0] == "price" else row[1]) for row in context.table
    }
    actual = context.response.json()
    for k, v in expected.items():
        if k == "price":
            # priceはDecimalとして返されるが、文字列として比較
            assert str(actual[k]) == str(v)
        else:
            assert actual[k] == v


@then('レスポンスJSONの{field}は"{value}"である')
def step_json_field_equals(context, field, value):
    data = context.response.json()
    if field == "price":
        expected = int(value)
        assert str(data[field]) == str(expected)
    else:
        assert data[field] == value


@then("レスポンスJSONの{field}は{value:d}である")
def step_json_field_equals_int(context, field, value):
    data = context.response.json()
    if field == "price":
        assert str(data[field]) == str(value)
    else:
        assert data[field] == value


@then('レスポンスJSONの{field}は"{value}"のままである')
def step_json_field_unchanged(context, field, value):
    data = context.response.json()
    if field == "price":
        expected = int(value)
        assert str(data[field]) == str(expected)
    else:
        assert data[field] == value


@then("レスポンスJSONの{field}は{value:d}のままである")
def step_json_field_unchanged_int(context, field, value):
    data = context.response.json()
    if field == "price":
        assert str(data[field]) == str(value)
    else:
        assert data[field] == value


@then("レスポンスJSONはサイズ{size:d}のリストである")
def step_json_list_size(context, size):
    data = context.response.json()
    assert isinstance(data, list)
    assert len(data) == size


@then("レスポンスJSONは次のアイテムを含む")
def step_json_contains_items(context):
    expected_items = [
        {
            heading: (int(row[heading]) if heading == "price" else row[heading])
            for heading in context.table.headings
        }
        for row in context.table
    ]
    actual = context.response.json()
    for exp in expected_items:
        match = next(
            (item for item in actual if item["product_id"] == exp["product_id"]), None
        )
        assert match, f"Expected item {exp['product_id']} not found"
        for k, v in exp.items():
            if k == "price":
                assert str(match[k]) == str(v)
            else:
                assert match[k] == v
