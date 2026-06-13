resource "aws_sqs_queue" "notification_dlq" {
  name = "${var.project_name}-notification-dlq-${var.environment}"
}

resource "aws_sqs_queue" "notification_queue" {
  name                       = "${var.project_name}-notification-${var.environment}"
  visibility_timeout_seconds = 60 # Match lambda timeout
  
  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.notification_dlq.arn
    maxReceiveCount     = 5
  })
}

resource "aws_sqs_queue" "enrichment_dlq" {
  name = "${var.project_name}-enrichment-dlq-${var.environment}"
}

resource "aws_sqs_queue" "enrichment_queue" {
  name                       = "${var.project_name}-enrichment-${var.environment}"
  visibility_timeout_seconds = 60
  
  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.enrichment_dlq.arn
    maxReceiveCount     = 5
  })
}
