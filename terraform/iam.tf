# Scraper Lambda IAM Role
resource "aws_iam_role" "scraper_lambda_role" {
  name = "${var.project_name}-scraper-role-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "scraper_basic_execution" {
  role       = aws_iam_role.scraper_lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_policy" "scraper_sqs_policy" {
  name        = "${var.project_name}-scraper-sqs-policy-${var.environment}"
  description = "Allows scraper lambda to publish to SQS"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "sqs:SendMessage"
        ]
        Resource = aws_sqs_queue.notification_queue.arn
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "scraper_sqs_attachment" {
  role       = aws_iam_role.scraper_lambda_role.name
  policy_arn = aws_iam_policy.scraper_sqs_policy.arn
}

# Notification Lambda IAM Role
resource "aws_iam_role" "notification_lambda_role" {
  name = "${var.project_name}-notification-role-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "notification_basic_execution" {
  role       = aws_iam_role.notification_lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_policy" "notification_sqs_policy" {
  name        = "${var.project_name}-notification-sqs-policy-${var.environment}"
  description = "Allows notification lambda to read from SQS"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "sqs:ReceiveMessage",
          "sqs:DeleteMessage",
          "sqs:GetQueueAttributes"
        ]
        Resource = aws_sqs_queue.notification_queue.arn
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "notification_sqs_attachment" {
  role       = aws_iam_role.notification_lambda_role.name
  policy_arn = aws_iam_policy.notification_sqs_policy.arn
}

resource "aws_iam_policy" "notification_ssm_policy" {
  name        = "${var.project_name}-notification-ssm-policy-${var.environment}"
  description = "Allows notification lambda to read SSM parameters"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ssm:GetParameter",
          "ssm:GetParameters"
        ]
        Resource = [
          aws_ssm_parameter.telegram_bot_token.arn,
          aws_ssm_parameter.telegram_chat_id.arn
        ]
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "notification_ssm_attachment" {
  role       = aws_iam_role.notification_lambda_role.name
  policy_arn = aws_iam_policy.notification_ssm_policy.arn
}
