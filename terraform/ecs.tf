data "aws_vpc" "default" {
  default = true
} 

data "aws_subnets" "time_capsule_subnets" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

resource "aws_cloudwatch_log_group" "time_capsule" {
  name = "time-capsule-tf-log-group"
  tags = {
    Environment = "production"
    Application = "Time Capsule"
  }
}

resource "aws_ecs_cluster" "time_capsule" {
  name = "time-capsule-tf-cluster"

  configuration {
    execute_command_configuration {
      logging    = "OVERRIDE"

      log_configuration {
        cloud_watch_encryption_enabled = true
        cloud_watch_log_group_name     = aws_cloudwatch_log_group.time_capsule.name
      }
    }
  }
}
resource "aws_security_group" "allow_tls_to_ecs" {
  name        = "allow_tls"
  description = "Allow TLS inbound traffic and all outbound traffic"
  vpc_id      = aws_vpc.default.id

  tags = {
    Name = "allow_tls"
  }
}

resource "aws_vpc_security_group_ingress_rule" "allow_full_to_ecs_ipv4" {
  security_group_id = aws_security_group.allow_tls_to_ecs.id
  cidr_ipv4         = "162.84.168.225/32"
  from_port         = 0
  ip_protocol       = -1
  to_port           = 0
}
resource "aws_vpc_security_group_ingress_rule" "allow_full_to_ecs_ipv4_from_home" {
  security_group_id = aws_security_group.allow_tls_to_ecs.id
  cidr_ipv4         = "68.237.105.18/32"
  from_port         = 0
  ip_protocol       = -1
  to_port           = 0
}
resource "aws_vpc_security_group_egress_rule" "allow_tls_to_ecs_ipv4" {
  security_group_id = aws_security_group.allow_tls_to_ecs.id
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "-1" # semantically equivalent to all ports
}

resource "aws_ecs_service" "time_capsule" {
  name            = "time-capsule-tf-service"
  cluster         = aws_ecs_cluster.time_capsule.id
  task_definition = aws_ecs_task_definition.time_capsule.arn
  desired_count   = 1
  # iam_role        = aws_iam_role.time_capsule_ecs_task_role.arn
  launch_type    = "FARGATE"

  # load_balancer {
  #   target_group_arn = aws_lb_target_group.time_capsule.arn
  #   container_name   = "time-capsule-tf-container"
  #   container_port   = 8080
  # }
  network_configuration {
    subnets          = data.aws_subnets.time_capsule_subnets.ids
    security_groups  = [aws_security_group.allow_tls_to_ecs.id]
    assign_public_ip = true
  }

}

data "aws_iam_policy" "AmazonECSTaskExecutionRolePolicy" {
  name = "AmazonECSTaskExecutionRolePolicy"
}

resource "aws_iam_role" "time_capsule_ecs_task_role" {
  name = "time-capsule-ecs-task-role-tf"
  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "ecs-tasks.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF

  tags = {
    Environment = "production"
    Application = "Time Capsule"
  }
  managed_policy_arns = [ data.aws_iam_policy.AmazonECSTaskExecutionRolePolicy.arn ]
}

resource "aws_ecs_task_definition" "time_capsule" {
  family                   = "time-capsule-tf-td"
  execution_role_arn       = aws_iam_role.time_capsule_ecs_task_role.arn
  task_role_arn            = aws_iam_role.time_capsule_ecs_task_role.arn
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu = 1024
  memory = 3072

  container_definitions = <<EOF
[
  {
    "name": "time-capsule-tf-container",
    "image": "926846101699.dkr.ecr.us-east-1.amazonaws.com/time-capsule-manual:latest",
    "cpu": 0,
    "portMappings": [
        {
            "name": "time-capsule-manual-container-80-tcp",
            "containerPort": 80,
            "hostPort": 80,
            "protocol": "tcp",
            "appProtocol": "http"
        }
    ],
    "essential": true,
    "environment": [],
    "environmentFiles": [],
    "mountPoints": [],
    "volumesFrom": [],
    "ulimits": [],
    "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "${aws_cloudwatch_log_group.time_capsule.name}",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        },
        "secretOptions": []
    }
  }
]
EOF

  tags = {
    Environment = "production"
    Application = "Time Capsule"
  }
}
