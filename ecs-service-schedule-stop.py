import boto3

def get_cluster_name_with_tag(tag_key, tag_value):
    ecs_client = boto3.client('ecs')

    try:
        print("Buscando clusters...")
        paginator = ecs_client.get_paginator('list_clusters')
        response_iterator = paginator.paginate()

        for page in response_iterator:
            cluster_arns = page['clusterArns']
            for arn in cluster_arns:
                cluster_info = ecs_client.describe_clusters(
                    clusters=[arn],
                    include=['TAGS']
                )
                cluster_tags = cluster_info['clusters'][0].get('tags', [])
                print(f"Cluster ARN: {arn}")
                print(f"Cluster tags: {cluster_tags}")
                
                # Verifica se a tag está presente e tem o valor correto
                if any(tag['key'] == tag_key and tag['value'] == tag_value for tag in cluster_tags):
                    print(f"Cluster encontrado com a tag '{tag_key}={tag_value}'!")
                    return cluster_info['clusters'][0]['clusterName']
        
        print(f"Nenhum cluster encontrado com a tag '{tag_key}={tag_value}'.")
        return None
    except Exception as e:
        print(f"Erro ao buscar o cluster: {str(e)}")
        return None

def list_cluster_services(cluster_name):
    ecs_client = boto3.client('ecs')
    
    try:
        response = ecs_client.list_services(
            cluster=cluster_name,
            maxResults=100  # Ajuste o valor conforme necessário para listar todos os serviços
        )
        return response.get('serviceArns', [])
    except Exception as e:
        print(f"Erro ao listar serviços: {str(e)}")
        return []

def store_replica_counts_in_dynamodb(replica_counts):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('ecs_services')  # Substitua 'NomeDaTabela' pelo nome da sua tabela no DynamoDB

    try:
        for service, count in replica_counts.items():
            response = table.put_item(
                Item={
                    'name_services': service,
                    'replica_counts': count
                }
            )
            print(f"Informações armazenadas para '{service}': {response}")
        return True
    except Exception as e:
        print(f"Erro ao armazenar no DynamoDB: {str(e)}")
        return False

def get_ecs_service_replica_count(cluster_name, services):
    ecs_client = boto3.client('ecs')
    
    try:
        replica_counts = {}
        response = ecs_client.describe_services(
            cluster=cluster_name,
            services=services
        )
        for service in response['services']:
            service_name = service['serviceName']
            running_count = service['runningCount']
            replica_counts[service_name] = running_count
        return replica_counts
    except Exception as e:
        return f"Error: {str(e)}"

def update_ecs_services(cluster_name, services, desired_count):
    ecs_client = boto3.client('ecs')

    for service in services:
        response = ecs_client.update_service(
            cluster=cluster_name,
            service=service,
            desiredCount=desired_count
        )

def lambda_handler(event, context):
    tag_key = 'Stop'
    tag_value = 'True'
    cluster_name = get_cluster_name_with_tag(tag_key, tag_value)  # Substitua pelo nome do seu cluster ECS22
    #services = ['teste']  # Substitua pelos nomes dos seus serviços ECS
    services = list_cluster_services(cluster_name)
    desired_count = 0  # Valor padrão para parar o serviço

    #Coleta o status atual do service
    replica_counts = get_ecs_service_replica_count(cluster_name, services)
    for service, replica_count in replica_counts.items():
        print(f"Número de réplicas em execução para o serviço '{service}' no cluster '{cluster_name}': {replica_count}")

    if replica_counts:
        success = store_replica_counts_in_dynamodb(replica_counts)
        if success:
            print("Informações armazenadas com sucesso no DynamoDB.")
        else:
            print("Falha ao armazenar informações no DynamoDB.")
    else:
        print("Não foi possível obter as contagens de réplicas dos serviços.")

    # Atualiza os serviços do ECS com a contagem desejada
    update_ecs_services(cluster_name, services, desired_count)
