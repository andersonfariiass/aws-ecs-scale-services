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
            print(cluster_info)
            for cluster in cluster_info['clusters']:
                name = cluster['clusterName']
                cluster_tags = cluster.get('tags', [])
                
                # Verifica se a tag está presente e tem o valor correto
                if any(tag['key'] == tag_key and tag['value'] == tag_value for tag in cluster_tags):
                    print(f"Cluster Name: {name}")
                    print(f"Cluster tags: {cluster_tags}")
                    print(f"Cluster encontrado com a tag '{tag_key}={tag_value}'!")
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
    service_names = []

    try:
        paginator = ecs_client.get_paginator('list_services')
        response_iterator = paginator.paginate(cluster=cluster_name)
        
        for page in response_iterator:
            service_arns = page['serviceArns']
            for arn in service_arns:
                service_name = arn.split('/')[-1]  # Extrai o nome do serviço do ARN
                service_names.append(service_name)
                
        return service_names
    except Exception as e:
        print(f"Erro ao listar serviços: {str(e)}")
        return []

def update_ecs_services(cluster_name, service_desired_counts):
    ecs_client = boto3.client('ecs')

    for service, desired_count in service_desired_counts.items():
        # Convertendo desired_count para int
        desired_count = int(desired_count)
        response = ecs_client.update_service(
            cluster=cluster_name,
            service=service,
            desiredCount=desired_count
        )

def retrieve_replica_counts_from_dynamodb():
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('ecs_services')  # Substitua 'NomeDaTabela' pelo nome da sua tabela no DynamoDB

    try:
        response = table.scan()
        replica_counts = {}
        for item in response['Items']:
            service_name = item['name_services']
            count = item['replica_counts']
            replica_counts[service_name] = count
        return replica_counts
    except Exception as e:
        print(f"Erro ao recuperar informações do DynamoDB: {str(e)}")
        return {}

def lambda_handler(event, context):
    tag_key = 'Start'
    tag_value = 'True'
    cluster_names = get_cluster_name_with_tag(tag_key, tag_value)
    for name in cluster_names:
        services = list_cluster_services(name)
        # Recupera as contagens de réplicas do DynamoDB
        replica_counts = retrieve_replica_counts_from_dynamodb()
        
        # Filtra as contagens de réplicas apenas para os serviços específicos
        desired_count = {service: replica_counts.get(service, 0) for service in services}
    
        # Atualiza os serviços do ECS com as contagens de réplicas recuperadas
        if desired_count:
            update_ecs_services(name, desired_count)
            for service, desired_count in desired_count.items():
                print(f"O serviço '{service}' do cluster {name} foi atualizado para {desired_count} réplicas.")
        else:
            print("Não foram encontradas contagens de réplicas no DynamoDB para os serviços especificados.")

