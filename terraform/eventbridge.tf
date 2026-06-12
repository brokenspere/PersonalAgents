# EventBridge rule for Market Open (9:30 AM EST -> 13:30 UTC or 14:30 UTC depending on DST. Using 13:30 for simplicity here)
resource "aws_cloudwatch_event_rule" "market_open_rule" {
  name                = "${var.project_name}-market-open-${var.environment}"
  description         = "Triggers scraper at market open"
  schedule_expression = "cron(30 13 ? * MON-FRI *)"
}

resource "aws_cloudwatch_event_target" "market_open_target" {
  rule      = aws_cloudwatch_event_rule.market_open_rule.name
  target_id = "ScraperFunction"
  arn       = aws_lambda_function.scraper_function.arn
  
  input = jsonencode({
    event_type = "market.open"
    market     = "NYSE"
  })
}

resource "aws_lambda_permission" "allow_eventbridge_open" {
  statement_id  = "AllowExecutionFromEventBridgeOpen"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.scraper_function.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.market_open_rule.arn
}

# EventBridge rule for Market Close (4:00 PM EST -> 20:00 UTC)
resource "aws_cloudwatch_event_rule" "market_close_rule" {
  name                = "${var.project_name}-market-close-${var.environment}"
  description         = "Triggers scraper at market close"
  schedule_expression = "cron(0 20 ? * MON-FRI *)"
}

resource "aws_cloudwatch_event_target" "market_close_target" {
  rule      = aws_cloudwatch_event_rule.market_close_rule.name
  target_id = "ScraperFunction"
  arn       = aws_lambda_function.scraper_function.arn
  
  input = jsonencode({
    event_type = "market.close"
    market     = "NYSE"
  })
}

resource "aws_lambda_permission" "allow_eventbridge_close" {
  statement_id  = "AllowExecutionFromEventBridgeClose"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.scraper_function.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.market_close_rule.arn
}
