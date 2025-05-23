Feature: 製品管理
  製品APIの利用者として
  製品の作成、取得、一覧表示、更新、削除を行い
  製品在庫を管理できるようにしたい

Background:
  Given 製品テーブルが空である

Scenario: 新しい製品を正常に作成
  When POSTリクエストを "/products/" に以下のJSONで送信するとき
    | product_id  | p1      |
    | name        | Prod1   |
    | description | Desc1   |
    | price       | 10      |
  Then レスポンスのステータスコードは200である
  And レスポンスJSONにフィールド "created_at" が含まれている
  And レスポンスJSONは次と一致する:
    | product_id  | p1      |
    | name        | Prod1   |
    | description | Desc1   |
    | price       | 10      |

Scenario: 重複した製品作成で409 Conflict
  Given product_id "p1" の製品が存在するとき
  When POSTリクエストを "/products/" に以下のJSONで送信するとき
    | product_id  | p1      |
    | name        | Prod1   |
    | description | Desc1   |
    | price       | 10      |
  Then レスポンスのステータスコードは409である

Scenario: 既存の製品を取得
  Given product_id "p1" の製品が存在するとき
  When GETリクエストを "/products/p1" に送信するとき
  Then レスポンスのステータスコードは200である
  And レスポンスJSONにフィールド "created_at" が含まれている
  And レスポンスJSONは次と一致する:
    | product_id  | p1      |
    | name        | Prod1   |
    | description | Desc1   |
    | price       | 10      |

Scenario Outline: 存在しない製品取得で404を返す
  When GETリクエストを "/products/<product_id>" に送信するとき
  Then レスポンスのステータスコードは404である

  Examples:
    | product_id   |
    | nonexistent  |
    | doesnotexist |

Scenario: 複数製品存在時の一覧取得
  Given 以下の製品が存在するとき:
    | product_id | name  | description | price |
    | p1         | Prod1 | Desc1       | 10    |
    | p2         | Prod2 | Desc2       | 20    |
  When GETリクエストを "/products/" に送信するとき
  Then レスポンスのステータスコードは200である
  And レスポンスJSONはサイズ2のリストである
  And レスポンスJSONは次のアイテムを含む:
    | product_id | name  | description | price |
    | p1         | Prod1 | Desc1       | 10    |
    | p2         | Prod2 | Desc2       | 20    |

Scenario: 製品の名前のみ更新
  Given product_id "p1" の製品が存在するとき
  When PATCHリクエストを "/products/p1" に以下のJSONで送信するとき
    | name | UpdatedName |
  Then レスポンスのステータスコードは200である
  And レスポンスJSONのnameは"UpdatedName"である
  And レスポンスJSONのdescriptionは"Desc1"のままである
  And レスポンスJSONのpriceは10のままである

Scenario: フィールド指定なしのPATCHで400エラー
  Given product_id "p1" の製品が存在するとき
  When PATCHリクエストを "/products/p1" に空のJSONで送信するとき
  Then レスポンスのステータスコードは400である

Scenario: 存在しない製品のPATCHで404を返す
  When PATCHリクエストを "/products/nonexistent" に以下のJSONで送信するとき
    | name | X |
  Then レスポンスのステータスコードは404である

Scenario: 複数フィールド更新
  Given product_id "p2" の製品が存在するとき
  When PATCHリクエストを "/products/p2" に以下のJSONで送信するとき
    | description | NewDesc |
    | price       | 99      |
  Then レスポンスのステータスコードは200である
  And レスポンスJSONのdescriptionは"NewDesc"である
  And レスポンスJSONのpriceは99である
  And レスポンスJSONのnameは"Prod2"のままである

Scenario: 既存製品の削除
  Given product_id "p1" の製品が存在するとき
  When DELETEリクエストを "/products/p1" に送信するとき
  Then レスポンスのステータスコードは204である

Scenario: 存在しない製品の削除で404を返す
  When DELETEリクエストを "/products/doesnotexist" に送信するとき
  Then レスポンスのステータスコードは404である
