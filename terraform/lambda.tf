# We use a dummy payload here for terraform to apply. 
# In reality, CI/CD will package the python code and update the lambda.

data "archive_file" "dummy_payload" {
  type        = "zip"
  output_path = "${path.module}/dummy_payload.zip"
  
  source {
    content  = "def lambda_handler(event, context):\n  pass"
    filename = "lambda_function.py"
  }
}

resource "aws_lambda_function" "scraper_function" {
  function_name    = "${var.project_name}-scraper-${var.environment}"
  role             = aws_iam_role.scraper_lambda_role.arn
  handler          = "workers.scraper.handlers.market_event_handler"
  runtime          = "python3.11"
  filename         = data.archive_file.dummy_payload.output_path
  source_code_hash = data.archive_file.dummy_payload.output_base64sha256
  timeout          = 30
  memory_size      = 256

  environment {
    variables = {
      ENRICHMENT_QUEUE_URL = aws_sqs_queue.enrichment_queue.url
      DEDUPLICATION_TABLE  = aws_dynamodb_table.scraper_cache.name
    }
  }
}

resource "aws_lambda_function" "enrichment_function" {
  function_name    = "${var.project_name}-enrichment-${var.environment}"
  role             = aws_iam_role.enrichment_lambda_role.arn
  handler          = "workers.enrichment.handlers.sqs_event_handler"
  runtime          = "python3.11"
  filename         = data.archive_file.dummy_payload.output_path
  source_code_hash = data.archive_file.dummy_payload.output_base64sha256
  timeout          = 60
  memory_size      = 512

  environment {
    variables = {
      ANALYST_QUEUE_URL = aws_sqs_queue.analyst_queue.url
    }
  }
}

resource "aws_lambda_event_source_mapping" "enrichment_sqs_trigger" {
  event_source_arn = aws_sqs_queue.enrichment_queue.arn
  function_name    = aws_lambda_function.enrichment_function.arn
  batch_size       = 1
}

resource "aws_lambda_function" "analyst_function" {
  function_name    = "${var.project_name}-analyst-${var.environment}"
  role             = aws_iam_role.analyst_lambda_role.arn
  handler          = "workers.analyst.handlers.sqs_event_handler"
  runtime          = "python3.11"
  filename         = data.archive_file.dummy_payload.output_path
  source_code_hash = data.archive_file.dummy_payload.output_base64sha256
  timeout          = 120
  memory_size      = 512

  environment {
    variables = {
      NOTIFICATION_QUEUE_URL = aws_sqs_queue.notification_queue.url
      GEMINI_API_KEY_SSM     = aws_ssm_parameter.gemini_api_key.name
    }
  }
}

resource "aws_lambda_event_source_mapping" "analyst_sqs_trigger" {
  event_source_arn = aws_sqs_queue.analyst_queue.arn
  function_name    = aws_lambda_function.analyst_function.arn
  batch_size       = 1
}

resource "aws_lambda_function" "notification_function" {
  function_name    = "${var.project_name}-notification-${var.environment}"
  role             = aws_iam_role.notification_lambda_role.arn
  handler          = "workers.notification.handlers.sqs_event_handler"
  runtime          = "python3.11"
  filename         = data.archive_file.dummy_payload.output_path
  source_code_hash = data.archive_file.dummy_payload.output_base64sha256
  timeout          = 60
  memory_size      = 256

  environment {
    variables = {
      TELEGRAM_BOT_TOKEN_SSM  = aws_ssm_parameter.telegram_bot_token.name
      TELEGRAM_CHAT_ID_SSM    = aws_ssm_parameter.telegram_chat_id.name
      # DISCORD_WEBHOOK_URL_SSM = aws_ssm_parameter.discord_webhook_url.name
    }
  }
}

# Event source mapping for SQS -> Notification Lambda
resource "aws_lambda_event_source_mapping" "notification_sqs_trigger" {
  event_source_arn = aws_sqs_queue.notification_queue.arn
  function_name    = aws_lambda_function.notification_function.arn
  batch_size       = 1
}

resource "aws_lambda_function" "screener_function" {
  function_name    = "${var.project_name}-screener-${var.environment}"
  role             = aws_iam_role.screener_lambda_role.arn
  handler          = "workers.screener.handlers.eventbridge_handler"
  runtime          = "python3.11"
  filename         = data.archive_file.dummy_payload.output_path
  source_code_hash = data.archive_file.dummy_payload.output_base64sha256
  timeout          = 120
  memory_size      = 512

  environment {
    variables = {
      NOTIFICATION_QUEUE_URL = aws_sqs_queue.notification_queue.url
      GEMINI_API_KEY_SSM     = aws_ssm_parameter.gemini_api_key.name
    }
  }
}
