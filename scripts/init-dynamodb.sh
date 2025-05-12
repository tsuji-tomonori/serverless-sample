#!/usr/bin/env sh
# DynamoDB Local が起動するまで待機する
until aws dynamodb list-tables --endpoint-url http://dynamodb-local:8000 > /dev/null 2>&1; do
    echo "Waiting for DynamoDB Local..."
    sleep 1
done

# テーブル作成（存在する場合はエラー無視）
aws dynamodb create-table \
    --table-name products \
    --attribute-definitions AttributeName=product_id,AttributeType=S \
    --key-schema AttributeName=product_id,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST \
    --endpoint-url http://dynamodb-local:8000 \
    || true

echo "DynamoDB table 'products' is ready."
