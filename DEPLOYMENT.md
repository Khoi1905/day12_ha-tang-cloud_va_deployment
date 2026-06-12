# Deployment Information

## Platform

Render Free Blueprint

## Public URL

https://day12-production-agent.onrender.com

## Public Endpoint Checks

```text
GET /       -> {"app":"Production AI Agent","version":"2.0.0"}
GET /health -> {"status":"ok", ...}
GET /ready  -> {"ready":true, ...}
```

## Environment Variables

- `AGENT_API_KEY`
- `ENVIRONMENT=production`
- `REDIS_URL`
- `RATE_LIMIT_PER_MINUTE=10`
- `MONTHLY_BUDGET_USD=10`

## Validation

```powershell
$env:BASE_URL = "https://day12-production-agent.onrender.com"
$env:AGENT_API_KEY = "<production-key>"
.\06-lab-complete\.venv\Scripts\python.exe -m pytest 06-lab-complete/tests -v
```

Secret không được ghi vào tài liệu hoặc commit vào repository.

### Health Check

```powershell
Invoke-RestMethod https://day12-production-agent.onrender.com/health
```

### Authenticated API Test

```powershell
$headers = @{
  "X-API-Key" = "<production-key>"
  "X-User-ID" = "student-01"
}
$body = '{"question":"What is Docker?"}'
Invoke-RestMethod https://day12-production-agent.onrender.com/ask `
  -Method Post -Headers $headers -ContentType application/json -Body $body
```

## Blueprint Resources

```text
day12-production-agent  -> Free Docker web service
day12-agent-cache       -> Free Render Key Value
REDIS_URL               -> Private connection string
```

## Screenshots

- [Deployment dashboard](screenshots/dashboard.png)
- [Service running](screenshots/running.png)
- [Cloud test results](screenshots/test.png)
