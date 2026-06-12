# Migrate to AWS Native Serverless Architecture for Cost Optimization

We decided to pivot from a containerized architecture (ECS Fargate + Redis + Celery) to an AWS Native Serverless architecture (Lambda + SQS + EventBridge) and switch from AWS Secrets Manager to SSM Parameter Store. 

**Why:** The primary goal for this personal project is extreme cost optimization. The containerized plan introduced baseline costs (NAT Gateways, ElastiCache nodes, Secrets Manager fees) that could easily exceed $45/month regardless of traffic. By adopting a serverless model:
- Compute (Lambda) is only billed for exact execution time (likely falling entirely within the free tier).
- Message brokering (SQS) and scheduling (EventBridge) scale to zero.
- Secrets are stored securely at zero cost using SSM Parameter Store (SecureString).
- Networking complexity is reduced as Lambdas running without a custom VPC have outbound internet access by default, eliminating the need for NAT Gateways.

This decision requires discarding the Celery orchestration developed in Phase 2 in favor of Lambda handler functions, but the long-term cost savings justify the refactoring effort.
