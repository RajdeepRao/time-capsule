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

resource "aws_ecs_service" "time_capsule" {
  name            = "time-capsule-tf-service"
  cluster         = aws_ecs_cluster.time_capsule.id
  task_definition = aws_ecs_task_definition.mongo.arn
  desired_count   = 1
  iam_role        = aws_iam_role.foo.arn
  depends_on      = [aws_iam_role_policy.foo]

  ordered_placement_strategy {
    type  = "binpack"
    field = "cpu"
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.foo.arn
    container_name   = "mongo"
    container_port   = 8080
  }

  placement_constraints {
    type       = "memberOf"
    expression = "attribute:ecs.availability-zone in [us-west-2a, us-west-2b]"
  }
}

resource "aws_iam_role" "foo" {
  name = "time-capsule-tf-role"
  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "ecs.amazonaws.com"
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
}
resource "aws_ecs_task_definition" "mongo" {
  family                   = "time-capsule-tf-task"
  execution_role_arn       = aws_iam_role.foo.arn
  task_role_arn            = aws_iam_role.foo.arn
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]

  container_definitions = <<EOF
[
  {
    "name": "mongo",
    "image": "mongo:latest",
    "portMappings": [
      {
        "containerPort": 27017,
        "protocol": "tcp"
      }
    ],
    "logConfiguration": {
      "logDriver": "awslogs",
      "options": {
        "awslogs-group": "${aws_cloudwatch_log_group.time_capsule.name}",
        "awslogs-region": "us-east-1",
        "awslogs-stream-prefix": "mongo"
      }
    }
  }
]
EOF

  tags = {
    Environment = "production"
    Application = "Time Capsule"
  }
}
