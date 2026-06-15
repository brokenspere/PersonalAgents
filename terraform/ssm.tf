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

# resource "aws_ssm_parameter" "discord_webhook_url" {
#   name        = "/${var.environment}/${var.project_name}/discord_webhook_url"
#   description = "Discord Webhook URL for notifications"
#   type        = "SecureString"
#   value       = "dummy_value_change_me"
# 
#   lifecycle {
#     ignore_changes = [value]
#   }
# }

resource "aws_ssm_parameter" "gemini_api_key" {
  name        = "/${var.environment}/${var.project_name}/gemini_api_key"
  description = "Google Gemini API Key for Analyst Agent"
  type        = "SecureString"
  value       = "dummy_value_change_me"

  lifecycle {
    ignore_changes = [value]
  }
}
