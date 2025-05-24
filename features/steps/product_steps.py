import json

import allure
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
    with allure.step("製品テーブルをクリア"):
        # 新しい TestClient を作成し、異なるテスト間でクリーンな状態を維持
        context.client = TestClient(app)
        # テーブルをクリア
        response = context.client.delete("/test/clear-table")

        allure.attach(
            f"ステータスコード: {response.status_code}",
            name="テーブルクリア結果",
            attachment_type=allure.attachment_type.TEXT,
        )


@given('product_id "{product_id}" の製品が存在するとき')
def step_product_exists(context, product_id):
    # 固定データで製品を作成
    data = PRODUCT_FIXTURES.get(product_id)
    assert data, f"Fixture not found for {product_id}"

    with allure.step(f"製品 {product_id} を事前作成"):
        resp = context.client.post("/products/", json=data)

        # リクエスト情報を添付
        allure.attach(
            json.dumps(data, ensure_ascii=False, indent=2),
            name="作成する製品データ",
            attachment_type=allure.attachment_type.JSON,
        )

        # レスポンス情報を添付
        allure.attach(
            f"ステータスコード: {resp.status_code}",
            name="レスポンスステータス",
            attachment_type=allure.attachment_type.TEXT,
        )

        try:
            response_json = resp.json()
            allure.attach(
                json.dumps(response_json, ensure_ascii=False, indent=2),
                name="作成された製品",
                attachment_type=allure.attachment_type.JSON,
            )
        except json.JSONDecodeError:
            allure.attach(
                resp.text,
                name="レスポンステキスト",
                attachment_type=allure.attachment_type.TEXT,
            )

        assert resp.status_code == 200, (
            f"製品作成に失敗: ステータスコード {resp.status_code}"
        )
        context.response = resp


@given("以下の製品が存在するとき")
def step_multiple_products_exist(context):
    with allure.step("複数の製品を事前作成"):
        for row in context.table:
            item = {
                "product_id": row["product_id"],
                "name": row["name"],
                "description": row.get("description"),
                "price": int(row["price"]),
            }

            with allure.step(f"製品 {item['product_id']} を作成"):
                resp = context.client.post("/products/", json=item)

                # リクエスト情報を添付
                allure.attach(
                    json.dumps(item, ensure_ascii=False, indent=2),
                    name=f"製品データ ({item['product_id']})",
                    attachment_type=allure.attachment_type.JSON,
                )

                # レスポンス情報を添付
                allure.attach(
                    f"ステータスコード: {resp.status_code}",
                    name=f"レスポンス ({item['product_id']})",
                    attachment_type=allure.attachment_type.TEXT,
                )

                assert resp.status_code == 200, (
                    f"製品 {item['product_id']} の作成に失敗: "
                    f"ステータスコード {resp.status_code}"
                )

        context.response = resp


@when('POSTリクエストを "{endpoint}" に以下のJSONで送信するとき')
def step_post_json(context, endpoint):
    # テーブルの各行を key, value のタプルとして取り出す
    payload = {}
    for row in context.table:
        field, raw_value = row.cells  # cells[0]=フィールド名, cells[1]=値
        # price は数値にキャスト、それ以外は文字列のまま
        payload[field] = int(raw_value) if field == "price" else raw_value

    # POSTリクエストを送信
    with allure.step(f"POSTリクエストを {endpoint} に送信"):
        # リクエスト情報を添付
        allure.attach(
            json.dumps(payload, ensure_ascii=False, indent=2),
            name="送信したJSONペイロード",
            attachment_type=allure.attachment_type.JSON,
        )

        context.response = context.client.post(endpoint, json=payload)

        # レスポンス情報を添付
        allure.attach(
            f"ステータスコード: {context.response.status_code}",
            name="レスポンスステータス",
            attachment_type=allure.attachment_type.TEXT,
        )

        # レスポンスボディがJSONの場合は添付
        try:
            response_json = context.response.json()
            allure.attach(
                json.dumps(response_json, ensure_ascii=False, indent=2),
                name="レスポンスJSON",
                attachment_type=allure.attachment_type.JSON,
            )
        except Exception:
            # JSONでない場合はテキストとして添付
            allure.attach(
                context.response.text,
                name="レスポンステキスト",
                attachment_type=allure.attachment_type.TEXT,
            )


@when('GETリクエストを "{endpoint}" に送信するとき')
def step_get(context, endpoint):
    with allure.step(f"GETリクエストを {endpoint} に送信"):
        context.response = context.client.get(endpoint)

        # レスポンス情報を添付
        allure.attach(
            f"URL: {endpoint}\nステータスコード: {context.response.status_code}",
            name="リクエスト情報",
            attachment_type=allure.attachment_type.TEXT,
        )

        # レスポンスボディがJSONの場合は添付
        try:
            response_json = context.response.json()
            allure.attach(
                json.dumps(response_json, ensure_ascii=False, indent=2),
                name="レスポンスJSON",
                attachment_type=allure.attachment_type.JSON,
            )
        except Exception:
            # JSONでない場合はテキストとして添付
            allure.attach(
                context.response.text,
                name="レスポンステキスト",
                attachment_type=allure.attachment_type.TEXT,
            )


@when('PATCHリクエストを "{endpoint}" に空のJSONで送信するとき')
def step_patch_empty(context, endpoint):
    context.response = context.client.patch(endpoint, json={})


@when('PATCHリクエストを "{endpoint}" に以下のJSONで送信するとき')
def step_patch_json(context, endpoint):
    # テーブルの各行を key, value のタプルとして取り出す
    payload = {}
    for row in context.table:
        field, raw_value = row.cells  # cells[0]=フィールド名, cells[1]=値
        # price は数値にキャスト、それ以外は文字列のまま
        payload[field] = int(raw_value) if field == "price" else raw_value

    # PATCHリクエストを送信
    context.response = context.client.patch(endpoint, json=payload)

    # Allureレポートにリクエスト・レスポンス情報を添付
    with allure.step(f"PATCHリクエストを {endpoint} に送信"):
        # リクエスト情報を添付
        allure.attach(
            json.dumps(payload, ensure_ascii=False, indent=2),
            name="送信したJSONペイロード",
            attachment_type=allure.attachment_type.JSON,
        )

        # レスポンス情報を添付
        allure.attach(
            f"ステータスコード: {context.response.status_code}",
            name="レスポンスステータス",
            attachment_type=allure.attachment_type.TEXT,
        )

        # レスポンスボディがJSONの場合は添付
        try:
            response_json = context.response.json()
            allure.attach(
                json.dumps(response_json, ensure_ascii=False, indent=2),
                name="レスポンスJSON",
                attachment_type=allure.attachment_type.JSON,
            )
        except Exception:
            # JSONでない場合はテキストとして添付
            allure.attach(
                context.response.text,
                name="レスポンステキスト",
                attachment_type=allure.attachment_type.TEXT,
            )


@when('DELETEリクエストを "{endpoint}" に送信するとき')
def step_delete(context, endpoint):
    with allure.step(f"DELETEリクエストを {endpoint} に送信"):
        context.response = context.client.delete(endpoint)

        # レスポンス情報を添付
        allure.attach(
            f"URL: {endpoint}\nステータスコード: {context.response.status_code}",
            name="リクエスト情報",
            attachment_type=allure.attachment_type.TEXT,
        )

        # レスポンスボディがある場合は添付
        if context.response.text:
            allure.attach(
                context.response.text,
                name="レスポンステキスト",
                attachment_type=allure.attachment_type.TEXT,
            )


@then("レスポンスのステータスコードは{status_code:d}である")
def step_status_code(context, status_code):
    actual_status = context.response.status_code

    with allure.step(f"ステータスコードが {status_code} であることを検証"):
        # ステータスコードの比較
        allure.attach(
            f"期待値: {status_code}\n実際の値: {actual_status}",
            name="ステータスコード比較",
            attachment_type=allure.attachment_type.TEXT,
        )

        # レスポンスの詳細情報
        allure.attach(
            f"URL: {context.response.url}\n"
            f"メソッド: {context.response.request.method}\n"
            f"ステータスコード: {actual_status}\n"
            f"ヘッダー: {dict(context.response.headers)}",
            name="レスポンス詳細",
            attachment_type=allure.attachment_type.TEXT,
        )

        # レスポンスボディを添付
        try:
            response_json = context.response.json()
            allure.attach(
                json.dumps(response_json, ensure_ascii=False, indent=2),
                name="レスポンスボディ (JSON)",
                attachment_type=allure.attachment_type.JSON,
            )
        except Exception:
            allure.attach(
                context.response.text or "(空のレスポンス)",
                name="レスポンスボディ (テキスト)",
                attachment_type=allure.attachment_type.TEXT,
            )

        # リクエストボディがある場合は添付
        if (
            hasattr(context.response.request, "content")
            and context.response.request.content
        ):
            try:
                request_json = json.loads(context.response.request.content)
                allure.attach(
                    json.dumps(request_json, ensure_ascii=False, indent=2),
                    name="リクエストボディ",
                    attachment_type=allure.attachment_type.JSON,
                )
            except Exception:
                pass

    # アサーション（詳細なエラーメッセージ付き）
    assert actual_status == status_code, (
        f"ステータスコードが期待値と異なります。\n"
        f"期待値: {status_code}\n"
        f"実際の値: {actual_status}\n"
        f"URL: {context.response.url}\n"
        f"レスポンス: {context.response.text}"
    )


@then('レスポンスJSONにフィールド "{field}" が含まれている')
def step_json_field(context, field):
    data = context.response.json()
    assert field in data


@then("レスポンスJSONは次と一致する")
def step_json_matches(context):
    # テーブルの各行を key, value のタプルとして取り出す
    expected = {}
    for row in context.table:
        field, raw_value = row.cells  # cells[0]=フィールド名, cells[1]=値
        # price は数値にキャスト、それ以外は文字列のまま
        expected[field] = int(raw_value) if field == "price" else raw_value

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
    actual_value = data.get(field)

    # Allureレポートに詳細情報を添付
    with allure.step(f"フィールド '{field}' の値を検証"):
        allure.attach(
            json.dumps(data, ensure_ascii=False, indent=2),
            name="実際のレスポンスJSON",
            attachment_type=allure.attachment_type.JSON,
        )
        allure.attach(
            f"期待値: {value}\n実際の値: {actual_value}",
            name="値の比較",
            attachment_type=allure.attachment_type.TEXT,
        )

    # 詳細なエラーメッセージを含むアサーション
    assert actual_value == value, (
        f"フィールド '{field}' の値が期待値と異なります。\n"
        f"期待値: {value}\n"
        f"実際の値: {actual_value}\n"
        f"レスポンス全体: {json.dumps(data, ensure_ascii=False, indent=2)}"
    )


@then('レスポンスJSONの{field}は"{value}"のままである')
def step_json_field_unchanged(context, field, value):
    data = context.response.json()
    actual_value = data.get(field)

    # Allureレポートに詳細情報を添付
    with allure.step(f"フィールド '{field}' の値が変更されていないことを検証"):
        allure.attach(
            json.dumps(data, ensure_ascii=False, indent=2),
            name="実際のレスポンスJSON",
            attachment_type=allure.attachment_type.JSON,
        )

        if field == "price":
            expected = int(value)
            allure.attach(
                f"期待値: {expected}\n実際の値: {actual_value}",
                name="値の比較",
                attachment_type=allure.attachment_type.TEXT,
            )
            assert str(actual_value) == str(expected), (
                f"フィールド '{field}' の値が期待値と異なります。\n"
                f"期待値: {expected}\n"
                f"実際の値: {actual_value}\n"
                f"レスポンス全体: {json.dumps(data, ensure_ascii=False, indent=2)}"
            )
        else:
            allure.attach(
                f"期待値: {value}\n実際の値: {actual_value}",
                name="値の比較",
                attachment_type=allure.attachment_type.TEXT,
            )
            assert actual_value == value, (
                f"フィールド '{field}' の値が期待値と異なります。\n"
                f"期待値: {value}\n"
                f"実際の値: {actual_value}\n"
                f"レスポンス全体: {json.dumps(data, ensure_ascii=False, indent=2)}"
            )


@then("レスポンスJSONの{field}は{value:d}のままである")
def step_json_field_unchanged_int(context, field, value):
    data = context.response.json()
    actual_value = data.get(field)

    # Allureレポートに詳細情報を添付
    with allure.step(f"フィールド '{field}' の値が変更されていないことを検証（整数）"):
        allure.attach(
            json.dumps(data, ensure_ascii=False, indent=2),
            name="実際のレスポンスJSON",
            attachment_type=allure.attachment_type.JSON,
        )
        allure.attach(
            f"期待値: {value}\n実際の値: {actual_value}",
            name="値の比較",
            attachment_type=allure.attachment_type.TEXT,
        )

    if field == "price":
        assert str(actual_value) == str(value), (
            f"フィールド '{field}' の値が期待値と異なります。\n"
            f"期待値: {value}\n"
            f"実際の値: {actual_value}\n"
            f"レスポンス全体: {json.dumps(data, ensure_ascii=False, indent=2)}"
        )
    else:
        assert actual_value == value, (
            f"フィールド '{field}' の値が期待値と異なります。\n"
            f"期待値: {value}\n"
            f"実際の値: {actual_value}\n"
            f"レスポンス全体: {json.dumps(data, ensure_ascii=False, indent=2)}"
        )


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
