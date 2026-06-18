resource "aws_cloudwatch_log_group" "scraper_lambda_log_group" {
  name              = "/aws/lambda/${aws_lambda_function.scraper_function.function_name}"
  retention_in_days = 1
}

resource "aws_cloudwatch_log_group" "notification_lambda_log_group" {
  name              = "/aws/lambda/${aws_lambda_function.notification_function.function_name}"
  retention_in_days = 1
}

resource "aws_cloudwatch_log_group" "analyst_lambda_log_group" {
  name              = "/aws/lambda/${aws_lambda_function.analyst_function.function_name}"
  retention_in_days = 1
}

resource "aws_cloudwatch_log_group" "enrichment_lambda_log_group" {
  name              = "/aws/lambda/${aws_lambda_function.enrichment_function.function_name}"
  retention_in_days = 1
}

resource "aws_cloudwatch_log_group" "screener_lambda_log_group" {
  name              = "/aws/lambda/${aws_lambda_function.screener_function.function_name}"
  retention_in_days = 1
}
