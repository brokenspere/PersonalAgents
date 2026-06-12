resource "aws_cloudwatch_log_group" "scraper_lambda_log_group" {
  name              = "/aws/lambda/${aws_lambda_function.scraper_function.function_name}"
  retention_in_days = 1
}

resource "aws_cloudwatch_log_group" "notification_lambda_log_group" {
  name              = "/aws/lambda/${aws_lambda_function.notification_function.function_name}"
  retention_in_days = 1
}
