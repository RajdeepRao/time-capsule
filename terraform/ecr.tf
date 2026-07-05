resource "aws_ecr_repository" "time_capsule" {
  name                 = "time-capsule"
  image_tag_mutability = "MUTABLE"
  force_delete         = true # dev: allow terraform destroy even with images present

  image_scanning_configuration {
    scan_on_push = true
  }
}

resource "aws_ecr_lifecycle_policy" "time_capsule" {
  repository = aws_ecr_repository.time_capsule.name
  policy = jsonencode({
    rules = [{
      rulePriority = 1
      description  = "Expire untagged images after 14 days"
      selection = {
        tagStatus   = "untagged"
        countType   = "sinceImagePushed"
        countUnit   = "days"
        countNumber = 14
      }
      action = { type = "expire" }
    }]
  })
}
