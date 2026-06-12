resource "aws_ssm_parameter" "telegram_bot_token" {
  name        = "/${var.environment}/${var.project_name}/telegram_bot_token"
  description = "Telegram Bot Token for notifications"
  type        = "SecureString"
  value       = "dummy_value_change_me"

  lifecycle {
    ignore_changes = [value]
  }
}

resource "aws_ssm_parameter" "telegram_chat_id" {
  name        = "/${var.environment}/${var.project_name}/telegram_chat_id"
  description = "Telegram Chat ID for notifications"
  type        = "SecureString"
  value       = "dummy_value_change_me"

  lifecycle {
    ignore_changes = [value]
  }
}
