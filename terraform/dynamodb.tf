resource "aws_dynamodb_table" "scraper_cache" {
  name           = "${var.project_name}-scraper-cache-${var.environment}"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "url"

  attribute {
    name = "url"
    type = "S"
  }

  ttl {
    attribute_name = "expires_at"
    enabled        = true
  }
}
