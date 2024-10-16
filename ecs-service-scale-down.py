import boto3

def get_cluster_name_with_tag(tag_key, tag_value):
    ecs_client = boto3.client('ecs')

    try:
        print("Buscando clusters...")
        paginator = ecs_client.get_paginator('list_clusters')
        response_iterator = paginator.paginate()
        cluster_names=[]

        for page in response_iterator:
            cluster_arns = page['clusterArns']
            cluster_info = ecs_client.describe_clusters(
                clusters=cluster_arns,
                include=['TAGS']
            )
            for cluster in cluster_info['clusters']:
                name = cluster['clusterName']
                cluster_tags = cluster.get('tags', [])
                
                # Verifica se a tag está presente e tem o valor correto
                if any(tag['key'] == tag_key and tag['value'] == tag_value for tag in cluster_tags):
                    print(f"Cluster encontrado com a tag '{tag_key}={tag_value}'!")
                    print(f"Cluster Name: {name}")
                    print(f"Cluster tags: {cluster_tags}")
                    cluster_names.append(name)
                print(cluster_names)
            return cluster_names
            
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

def store_replica_counts_in_dynamodb(replica_counts, cluster_name):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('ecs_state_services') 

    try:
        for service, count in replica_counts.items():
            response = table.put_item(
                Item={
                    'name_services': service,
                    'replica_counts': count,
                    'cluster_name': cluster_name
                }
            )
            print(f"Informações armazenadas para '{service}': {response}")
        return True
    except Exception as e:
        print(f"Erro ao armazenar no DynamoDB: {str(e)}")
        return False

def get_ecs_service_replica_count(cluster_name, services):
    ecs_client = boto3.client('ecs')
    
    # try:
    #     replica_counts = {}
    #     response = ecs_client.describe_services(
    #         cluster=cluster_name,
    #         services=services
    #     )
    #     for service in response['services']:
    #         service_name = service['serviceName']
    #         running_count = service['runningCount']
    #         replica_counts[service_name] = running_count
    #     return replica_counts
    try:
    replica_counts = {}
    for service in services:
        response = ecs_client.describe_services(
            cluster=cluster_name,
            services=[service]
        )
        current_service = response['services'][0]
        service_name = current_service['serviceName']
        running_count = current_service['runningCount']
        replica_counts[service_name] = running_count
    return replica_counts
    except Exception as e:
        return f"Error: {str(e)}"

def update_ecs_services(cluster_name, services, desired_count):
    ecs_client = boto3.client('ecs')
    
    for service in services:
        print(f"Realizando scale-down do serviço: '{service}'")
        response = ecs_client.update_service(
            cluster=cluster_name,
            service=service,
            desiredCount=desired_count
        )
        print(f"Número de réplicas do '{service}' no cluster '{cluster_name}' atualizado para {desired_count} réplicas")
    print(f"scale-down no cluster '{cluster_name} finalizado'")
    print()

def lambda_handler(event, context):
    tag_key = 'Stop'
    tag_value = 'True'
    desired_count = 0
    cluster_names = get_cluster_name_with_tag(tag_key, tag_value)
    for name in cluster_names:
        services = list_cluster_services(name)
        #Coleta o status atual do service
        replica_counts = get_ecs_service_replica_count(name, services)
        for service, replica_count in replica_counts.items():
            print(f"Número de réplicas em execução para o serviço '{service}' no cluster '{name}': {replica_count}")
    
        if replica_counts:
            success = store_replica_counts_in_dynamodb(replica_counts, name)
            if success:
                update_ecs_services(name, services, desired_count)
                print("Informações armazenadas com sucesso no DynamoDB.")
            else:
                print("Falha ao armazenar informações no DynamoDB, o update service não pode ser executado")
        else:
            print("Não foi possível obter as contagens de réplicas dos serviços.")