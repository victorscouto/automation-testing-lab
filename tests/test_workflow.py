import json
import os
import time
import boto3
import pytest

AWS_ENDPOINT = os.getenv("AWS_ENDPOINT_URL", "http://localhost:4566")

@pytest.fixture
def aws_setup():
    # Inicializa clientes apontando para o MiniStack / porta 4566
    s3 = boto3.client('s3', endpoint_url=AWS_ENDPOINT, aws_access_key_id='test', aws_secret_access_key='test', region_name='us-east-1')
    sfn = boto3.client('stepfunctions', endpoint_url=AWS_ENDPOINT, aws_access_key_id='test', aws_secret_access_key='test', region_name='us-east-1')
    
    # Cria os buckets de origem e destino
    s3.create_bucket(Bucket='bucket-origem')
    s3.create_bucket(Bucket='bucket-destino')
    
    # Insere dados iniciais no bucket de origem
    sample_data = {"id": 123, "payload": "dados de teste via step function"}
    s3.put_object(Bucket='bucket-origem', Key='input/dados.json', Body=json.dumps(sample_data))
    
    return s3, sfn

def test_step_function_end_to_end(aws_setup):
    s3, sfn = aws_setup
    
    # Nota: Em um ambiente de CI/CD completo, você faria o deploy/criação da State Machine aqui 
    # ou utilizaria o container oficial do Step Functions Local se a máquina for complexa.
    # Exemplo simulando o disparo da execução da Step Function:
    
    input_payload = {
        "source_bucket": "bucket-origem",
        "source_key": "input/dados.json",
        "dest_bucket": "bucket-destino",
        "dest_key": "output/resultado-sf.json"
    }
    
    # Se a State Machine já estiver provisionada no MiniStack:
    # state_machine_arn = "arn:aws:states:us-east-1:000000000000:stateMachine:MeuWorkflow"
    # execution = sfn.start_execution(
    #     stateMachineArn=state_machine_arn,
    #     input=json.dumps(input_payload)
    # )
    # execution_arn = execution['executionArn']
    
    # # Aguarda a conclusão da execução (Polling de status)
    # while True:
    #     desc = sfn.describe_execution(executionArn=execution_arn)
    #     status = desc['status']
    #     if status == 'SUCCEEDED':
    #         break
    #     elif status in ['FAILED', 'TIMED_OUT', 'ABORTED']:
    #         pytest.fail(f"Step Function falhou com status: {status}")
    #     time.sleep(1)

    # Validando o resultado gravado no bucket de destino S3 pela Lambda orquestrada
    obj = s3.get_object(Bucket='bucket-destino', Key='output/resultado-sf.json')
    result_data = json.loads(obj['Body'].read().decode('utf-8'))
    
    assert result_data['id'] == 123
    assert result_data['processed'] is True
    assert result_data['status'] == 'COMPLETED'
