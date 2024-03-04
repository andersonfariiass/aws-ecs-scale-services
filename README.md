# ecs-schedule-services

Este projeto demonstra como usar AWS Lambda e Amazon EventBridge para agendar o aumento e a redução da capacidade dos serviços do Amazon ECS (Elastic Container Service) com launch type Fargate, baseando-se em tags específicas. Os serviços do ECS serão escalonados de acordo com as tags "Start=True" e "Stop=True" atribuídas aos clusters ECS.


