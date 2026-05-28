resource "aws_ecs_cluster" "main" {
  name = "${var.project_prefix}-cluster-${var.environment}"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }

  tags = { Environment = var.environment }
}

resource "aws_service_discovery_private_dns_namespace" "main" {
  name = "${var.project_prefix}.internal"
  vpc  = var.vpc_id
}

# Create task definition + service for each microservice
resource "aws_ecs_task_definition" "services" {
  for_each = var.service_images

  family                   = "${var.project_prefix}-${each.key}-${var.environment}"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.cpu
  memory                   = var.memory
  execution_role_arn       = var.ecs_execution_role_arn
  task_role_arn            = var.service_task_role_arns[each.key]

  container_definitions = jsonencode([{
    name      = each.key
    image     = each.value
    essential = true
    portMappings = [{ containerPort = 8000, protocol = "tcp" }]
    environment = var.service_env_vars[each.key]
    logConfiguration = {
      logDriver = "awslogs"
      options = {
        "awslogs-group"         = "/${var.project_prefix}/${var.environment}/${each.key}"
        "awslogs-region"        = var.aws_region
        "awslogs-stream-prefix" = "ecs"
      }
    }
  }])
}

resource "aws_service_discovery_service" "services" {
  for_each = var.service_images

  name = each.key

  dns_config {
    namespace_id = aws_service_discovery_private_dns_namespace.main.id
    dns_records {
      ttl  = 10
      type = "A"
    }
  }
}

resource "aws_ecs_service" "services" {
  for_each = var.service_images

  name            = "${var.project_prefix}-${each.key}-${var.environment}"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.services[each.key].arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = var.private_subnet_ids
    security_groups  = [var.ecs_security_group_id]
    assign_public_ip = false
  }

  service_registries {
    registry_arn = aws_service_discovery_service.services[each.key].arn
  }

  tags = { Service = each.key, Environment = var.environment }
}
