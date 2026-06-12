# Day 12 Lab - Mission Answers

## Part 1: Localhost vs Production

### Exercise 1.1: Anti-patterns

1. API key và database credential bị hardcode.
2. Secret bị ghi ra log.
3. App bind vào `localhost`, container bên ngoài không truy cập được.
4. Port cố định thay vì đọc biến `PORT`.
5. Bật debug reload trong production.
6. Không có health/readiness endpoint.
7. Dùng `print()` thay vì structured logging.
8. Không quản lý startup và graceful shutdown.

### Exercise 1.2: Chạy basic version

Basic agent chạy được trên localhost nhưng chỉ phù hợp development vì bind
`localhost`, bật reload, thiếu probes và chứa config nhạy cảm trong source.

### Exercise 1.3: So sánh

| Feature | Develop | Production | Tại sao quan trọng |
|---|---|---|---|
| Config | Hardcode | Environment variables | Một image chạy được ở nhiều môi trường |
| Health | Không có | `/health`, `/ready` | Platform biết restart hoặc ngừng route |
| Logging | `print()` | JSON event log | Log aggregator parse được |
| Shutdown | Đột ngột | Uvicorn graceful shutdown | Hoàn thành request đang chạy |
| Network | `localhost` | `0.0.0.0` | Nhận traffic ngoài container |

## Part 2: Docker

### Exercise 2.1: Dockerfile questions

1. Basic base image: `python:3.11`.
2. Working directory: `/app`.
3. Copy `requirements.txt` trước để tận dụng Docker layer cache.
4. `CMD` cung cấp command mặc định và dễ override; `ENTRYPOINT` định nghĩa executable chính.

### Exercise 2.2: Build và run

Basic container đóng gói Python, dependencies và source code, loại bỏ khác biệt
môi trường giữa máy development và nơi deploy.

### Exercise 2.3: Multi-stage build

5. Final image dùng multi-stage, slim runtime và non-root user.
6. Image production cuối lab: khoảng **253 MB**, dưới yêu cầu 500 MB.

Builder stage cài dependencies; runtime stage chỉ giữ package và source cần để
chạy, giúp giảm kích thước và attack surface.

### Exercise 2.4: Docker Compose architecture

Stack cuối:

```text
Nginx -> 3 Agent replicas -> Redis
```

## Part 3: Cloud Deployment

### Exercise 3.1-3.2: Public deployment

- Render Free được chọn vì hỗ trợ Docker web service, Key Value tương thích
  Redis và public HTTPS URL mà không cần phương thức thanh toán.
- Root-level `render.yaml` tạo cả web service và Key Value instance.
- `REDIS_URL` được lấy tự động từ private connection string của Key Value.
- `AGENT_API_KEY` được nhập dưới dạng secret, không commit vào Git.
- Public deployment: `https://day12-production-agent.onrender.com`.

Render Blueprint dùng `render.yaml`; Railway dùng `railway.toml`. Cả hai đều
mô tả cách build/start và health check, nhưng Blueprint còn khai báo được cả
web service và Key Value dependency trong cùng file.

### Exercise 3.3: Cloud Run CI/CD

- Cloud Run example trong lab minh họa build/push/deploy CI/CD pipeline nâng cao.

## Part 4: API Security

### Exercise 4.1: API key authentication

- API key được đọc từ `X-API-Key` và so sánh constant-time.
- `X-User-ID` mô phỏng caller identity; production thực tế nên dùng JWT subject.

Không có key hoặc key sai trả HTTP `401`. Rotate key bằng cách cập nhật secret
`AGENT_API_KEY` trên platform rồi redeploy.

### Exercise 4.2: JWT authentication

Ví dụ nâng cao tại `04-api-gateway/production/auth.py` phát hành JWT có subject,
role và expiration; mỗi request verify chữ ký và expiry trước khi xử lý.

### Exercise 4.3: Rate limiting

- Rate limiter dùng Redis sorted set và Lua script atomic.
- Limit mặc định là 10 request/phút/user; request tiếp theo trả `429`.

Lua script giúp nhiều instance kiểm tra và ghi request trong một thao tác atomic.

### Exercise 4.4: Cost guard

- Cost guard dùng Redis và Lua script atomic, budget mặc định `$10/tháng/user`.
- API trả `402` nếu request mới làm vượt budget.

## Part 5: Scaling & Reliability

### Exercise 5.1: Health và readiness

- `/health` kiểm tra process sống.
- `/ready` kiểm tra app đã startup và Redis còn kết nối.

### Exercise 5.2: Graceful shutdown

- Uvicorn xử lý SIGTERM, chờ in-flight requests rồi chạy lifespan cleanup.

### Exercise 5.3: Stateless design

- Conversation, rate limit và cost đều nằm trong Redis.

### Exercise 5.4: Load balancing

- Nginx phân phối request tới 3 instance.

### Exercise 5.5: Stateless test

- Kết quả local: cả 3 instance đã phục vụ request, session vẫn nhất quán.
- Sau khi dừng instance xử lý turn đầu, turn tiếp theo được instance khác xử lý
  và vẫn trả đúng conversation context.

## Part 6: Final Project

Implementation nằm trong `06-lab-complete/`.

Kết quả kiểm thử local:

```text
3 agent replicas healthy
Redis healthy
Nginx exposed at localhost:8000
5/5 black-box tests passed
Cost guard returned HTTP 402 at the configured budget
Session continued after one serving instance was stopped
Docker image size: 253 MB
```

Các test xác minh health/readiness, auth, Redis conversation history và shared
rate limit qua nhiều instance. Conversation context test yêu cầu agent nhắc lại
đúng câu hỏi trước đó từ history lưu trong Redis.
