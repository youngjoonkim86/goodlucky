# Frontend API 연결 문제 해결

## 문제
Frontend가 `localhost:8000`으로 API 요청을 보내고 있었지만, Backend는 `localhost:8001`에서 실행 중이었습니다.

## 해결 방법

### 1. API URL 수정
`frontend/src/services/api.ts` 파일에서 기본 URL을 수정했습니다:
```typescript
// 수정 전
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

// 수정 후
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8001/api/v1'
```

### 2. CORS 설정 업데이트
`backend/app/core/config.py`에서 Frontend 포트를 추가했습니다:
```python
CORS_ORIGINS: List[str] = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:3002",  # 추가됨
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3002",  # 추가됨
]
```

### 3. Docker Compose 환경변수 수정
`docker-compose.minimal.yml`에서 환경변수 이름을 수정했습니다:
```yaml
environment:
  - VITE_API_URL=http://localhost:8001  # REACT_APP_API_URL -> VITE_API_URL
```

## 브라우저에서 확인

1. **하드 리프레시**: `Ctrl + Shift + R` (Windows) 또는 `Cmd + Shift + R` (Mac)
2. **브라우저 캐시 삭제**: 개발자 도구 > Network 탭 > "Disable cache" 체크
3. **새로고침**: 페이지를 새로고침하여 변경사항 적용

## 현재 접속 정보

- **Frontend**: http://localhost:3002
- **Backend API**: http://localhost:8001
- **API 문서**: http://localhost:8001/docs

## 추가 확인 사항

만약 여전히 404 오류가 발생한다면:

1. **브라우저 콘솔 확인**: 개발자 도구에서 실제 요청 URL 확인
2. **Network 탭 확인**: 요청이 올바른 포트로 가는지 확인
3. **Backend 로그 확인**: 
   ```bash
   docker-compose -f docker-compose.minimal.yml logs backend --tail 20
   ```

