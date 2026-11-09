import json
import os
import boto3

s3_client = boto3.client('s3')

def lambda_handler(event, context):
    source_bucket = event.get('source_bucket')
    source_key = event.get('source_key')
    dest_bucket = event.get('dest_bucket')
    dest_key = event.get('dest_key')

    # 1. Lê o arquivo do bucket de origem
    response = s3_client.get_object(Bucket=source_bucket, Key=source_key)
    file_content = response['Body'].read().decode('utf-8')
    data = json.loads(file_content)

    # 2. Processa os dados (exemplo: adiciona metadados de processamento)
    data['processed'] = True
    data['status'] = 'COMPLETED'

    # 3. Escreve o resultado no bucket de destino
    s3_client.put_object(
        Bucket=dest_bucket,
        Key=dest_key,
        Body=json.dumps(data),
        ContentType='application/json'
    )

    return {
        'statusCode': 200,
        'body': json.dumps('Processamento concluído com sucesso!')
    }
