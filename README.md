# ecs-schedule-services

Este projeto demonstra como usar AWS Lambda e Amazon EventBridge para agendar o aumento e a redução da capacidade dos serviços do Amazon ECS (Elastic Container Service) com launch type Fargate, baseando-se em tags específicas. Os serviços do ECS serão escalonados de acordo com as tags "Start=True" e "Stop=True" atribuídas aos clusters ECS.

## Funcionamento

Lambda ecs-services-schedule-stop:
Esta função Lambda é acionada por um evento agendado (usando o Amazon EventBridge) para zerar as réplicas dos serviços ECS. Ele verifica os clusters ECS com a tag "Stop=True", e salva o Estado dos Serviços no DynamoDB antes de zera as replicas do serviços do ecs:
Antes de reduzir a capacidade dos serviços ECS, o estado atual dos serviços (número de réplicas em execução) será salvo em uma tabela do Amazon DynamoDB. Isso é feito para que o estado anterior possa ser restaurado durante a execução da lambda ecs-services-schedule-star.

Lambda ecs-services-schedule-star:
Esta função Lambda é acionada por um evento agendado (usando o Amazon EventBridge) para aumentar as replicas dos serviços ECS. Ele verifica os clusters ECS com a tag "Start=True" e ajusta a capacidade de acordo com as informações que foram armazenadas no dynamoDB pela lambda ecs-services-schedule-stop.

