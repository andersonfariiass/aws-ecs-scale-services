# ECS Fargate Scale Services
Este projeto demonstra como usar AWS Lambda e Amazon EventBridge para agendar o aumento e a redução da capacidade dos serviços do Amazon ECS (Elastic Container Service) com launch type Fargate, baseando-se em tags específicas. Os serviços do ECS serão escalonados de acordo com as tags "Start=True" e "Stop=True" atribuídas aos clusters ECS.
O Objetivo dessa solução é reduzir custos com clusters ECS não produtivos, onde não há a necessidade de ficarem disponiveis 24x7.

Fluxo para scale-down dos services:
<img src="/images/ecs-services-scale-down.jpg">

Fluxo para scale-up dos services:
<img src="/images/ecs-services-scale-up.jpg">

## Funcionamento

Lambda ecs-services-scale-down:
Esta função Lambda é acionada por um evento agendado (usando o Amazon EventBridge) para zerar as réplicas dos serviços ECS. Ele verifica os clusters ECS com a tag "Stop=True", e salva o Estado dos Serviços no DynamoDB antes de zera as replicas do serviços do ecs.
Antes de reduzir as réplicas dos serviços ECS, o estado atual dos serviços (número de réplicas em execução) será salvo em uma tabela do Amazon DynamoDB. Isso é feito para que o estado anterior possa ser restaurado durante a execução da lambda ecs-services-scale-up.

Lambda ecs-services-scale-up:
Esta função Lambda é acionada por um evento agendado (usando o Amazon EventBridge) para aumentar as replicas dos serviços ECS. Ele verifica os clusters ECS com a tag "Start=True" e ajusta a capacidade de acordo com as informações que foram armazenadas no dynamoDB pela lambda ecs-services-scale-down.

## Requisitos

- Lambda ecs-services-scale-down:
Configure uma função Lambda que reduz a capacidade dos serviços ECS quando acionada por um evento agendado do EventBridge.
A função deve verificar os clusters ECS com a tag "Stop=True" e reduzir a capacidade dos serviços conforme necessário.
Amazon EventBridge Rules:

- Lambda ecs-services-scale-up:
Configure uma função Lambda que aumenta a capacidade dos serviços ECS quando acionada por um evento agendado do EventBridge.
A função deve verificar os clusters ECS com a tag "Start=True" e aumentar a capacidade dos serviços conforme necessário.

- Defina regras no Amazon EventBridge para acionar as funções Lambda de acordo com uma programação definida. Configure as regras para acionar as funções Lambda nos horários desejados.

- Permissões:
Certifique-se de que as funções Lambda tenham permissões adequadas para interagir com os serviços ECS, o Amazon EventBridge e o DynamoDB.<br />
Garanta que a Role usada nas lambdas tenha as seguintes permissões:
    - 'dynamodb:PutItem'
    - 'dynamodb:GetItem'
    - 'dynamodb:UpdateItem'
    - 'dynamodb:Scan'
    - 'ecs:ListServices'
    - 'ecs:UpdateService'
    - 'ecs:ListAttributes'
    - 'ecs:ListTasks'
    - 'ecs:DescribeServices'
    - 'ecs:DescribeClusters'
    - 'ecs:ListClusters'

- Tags ECS:
Atribua as tags "Start=True" e "Stop=True" aos clusters ECS conforme necessário. Certifique-se de atribuir essas tags aos clusters ECS que você deseja controlar.


