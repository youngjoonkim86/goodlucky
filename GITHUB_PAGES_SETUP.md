# GitHub Pages 배포 설정 가이드

## ✅ 완료된 작업

1. ✅ GitHub 저장소에 코드 푸시 완료
2. ✅ GitHub Actions 워크플로우 설정 완료
3. ✅ Vite 설정에 base 경로 추가 완료

## 🔧 GitHub Pages 활성화 방법

### 1단계: GitHub 저장소 설정

1. GitHub 저장소로 이동: https://github.com/youngjoonkim86/goodlucky
2. **Settings** 탭 클릭
3. 왼쪽 메뉴에서 **Pages** 클릭

### 2단계: Pages 설정

1. **Source** 섹션에서:
   - **Source** 드롭다운을 "**GitHub Actions**"로 선택
   - (기존 "Deploy from a branch"가 선택되어 있다면 변경)

2. **Save** 버튼 클릭

### 3단계: 자동 배포 확인

- `main` 브랜치에 푸시할 때마다 자동으로 배포됩니다
- Actions 탭에서 배포 진행 상황을 확인할 수 있습니다
- 배포 완료 후 약 1-2분 후 다음 URL로 접근 가능:
  - **https://youngjoonkim86.github.io/goodlucky**

## 📝 참고사항

### 백엔드 API 설정

GitHub Pages는 정적 사이트만 호스팅하므로, 백엔드 API는 별도로 배포해야 합니다.

**옵션 1: 무료 백엔드 호스팅**
- **Railway**: https://railway.app
- **Render**: https://render.com
- **Fly.io**: https://fly.io

**옵션 2: 환경 변수로 API URL 설정**

프론트엔드 빌드 시 백엔드 API URL을 환경 변수로 설정:

```bash
# GitHub Actions Secrets에 추가
VITE_API_URL=https://your-backend-api.com/api/v1
```

### 현재 상태

- ✅ 프론트엔드: GitHub Pages에 배포 준비 완료
- ⚠️ 백엔드: 별도 배포 필요 (위 옵션 참고)

## 🚀 배포 확인

배포가 완료되면:
1. https://youngjoonkim86.github.io/goodlucky 접속
2. 페이지가 정상적으로 로드되는지 확인

## 🔄 자동 배포

이제 `main` 브랜치에 푸시할 때마다 자동으로 배포됩니다:

```bash
git add .
git commit -m "Update"
git push origin main
```

## ❓ 문제 해결

### 배포가 안 될 때
1. GitHub Actions 탭에서 에러 확인
2. Pages 설정에서 Source가 "GitHub Actions"인지 확인
3. 저장소가 Public인지 확인 (Private 저장소는 유료 플랜 필요)

### 페이지가 404 에러일 때
1. 배포가 완료될 때까지 기다리기 (1-2분)
2. 브라우저 캐시 삭제 후 재시도
3. URL이 정확한지 확인: `/goodlucky/`로 끝나야 함

