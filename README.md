# PNU CSE Notice Checker

부산대학교 정보컴퓨터공학부 공지사항을 매일 자동으로 모니터링하여 새 공지가 있을 경우 이메일로 알려주는 자동화 봇입니다.

## 기능

- 매일 오전 10시 (KST) 공지사항 페이지 자동 크롤링
- 새 공지가 있을 때만 이메일 발송 (없으면 발송 안 함)
- GitHub Actions 기반으로 완전 무료로 동작

## 동작 방식

1. GitHub Actions가 매일 오전 10시에 자동 실행
2. 부산대 CSE 공지사항 페이지 크롤링
3. `last_seen.json`에 저장된 마지막 공지 번호와 비교
4. 새 공지가 있으면 이메일 발송 후 번호 업데이트

## 설정 방법

GitHub 레포 → Settings → Secrets and variables → Actions에 아래 3개 등록

| 이름 | 설명 |
|------|------|
| `EMAIL_SENDER` | 보내는 Gmail 주소 |
| `EMAIL_PASSWORD` | Gmail 앱 비밀번호 |
| `EMAIL_RECEIVER` | 받을 이메일 주소 |

---

## 개발 중 발생한 오류 및 해결

### 1. 크롤링 선택자 오류

**문제**
부산대 공지사항 페이지의 HTML 구조를 사전에 확인하지 못하고 일반적인 대학 포털 구조를 추측하여 `td.td-subject` 선택자를 사용했습니다. 그러나 실제 사이트의 선택자는 `td.td-title`이었기 때문에 공지를 전혀 가져오지 못했습니다.

**해결**
GitHub Actions 로그에 HTML을 출력하여 실제 구조를 확인한 후 선택자를 `td.td-title`로 수정했습니다.

---

### 2. `last_seen.json` 자동 push 실패

**문제**
초기에 `stefanzweifel/git-auto-commit-action` 플러그인을 사용하여 `last_seen.json`을 자동으로 커밋/push하도록 구성했으나, 레포의 쓰기 권한 문제로 인해 push가 되지 않았습니다. 그 결과 `last_seen.json`이 계속 `{}`인 상태로 남아 공지 번호가 저장되지 않았습니다.

**해결**
외부 플러그인 의존을 제거하고, Python 코드 내에서 직접 `subprocess`로 `git add`, `git commit`, `git push`를 실행하는 방식으로 변경하여 해결했습니다.
