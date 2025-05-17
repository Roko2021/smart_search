## Search API

### Authentication
1. Get token:
```bash
curl -X POST http://localhost:8000/api/token/ \
-H "Content-Type: application/json" \
-d '{"username":"admin","password":"admin"}'