# Musinsa Rulebook — 팀이 함께 키우는 Codex 코딩 룰북

> 한 사람이 어렵게 배운 교훈을 캡처해, **모두의 AI 에이전트에 자동으로 강제**하는 Codex 플러그인.
> 무신사가 기술블로그에 공개한 엔지니어링 교훈을 기본 규칙(seed)으로 탑재하고, 팀이 `/remember`로 규칙을 계속 키워 `/review`로 PR을 검수·채점한다.

## 설치 (Codex)

```bash
codex plugin marketplace add KimDaeHyun00/musinsa-rulebook
# Codex 안에서:
/plugins                 # → "musinsa-rulebook" 설치 → 활성화
pip install pyyaml       # 룰북 스캐너(check.py) 의존성
```
사용: `@remember "<규칙>"` 으로 규칙 추가, `@review` 로 변경분 채점. (자연어로도 트리거)

---

## 1. 무엇을, 누가, 어떤 상황에서 쓰나

- **누가:** 이미 Codex로 일하는 무신사(및 패션커머스) 백엔드 개발자.
- **언제:**
  - 버그를 고친 뒤 → `/remember "이 실수 다신 하지 말 것"` 으로 팀 룰북에 규칙 추가
  - PR 올리기 직전 → `/review` 로 변경분이 팀 룰을 어기는지 점검 + 점수 확인
- **무엇이 달라지나:** "이 코드 먼저 파악하고, 우리 인덱스 규칙 지키고, 이런 실수 하지 마"를 매번 사람이 타이핑하던 걸, 룰북에 누적된 **팀의 집단 판단력**이 에이전트 안에서 자동 처리한다.

## 2. 왜 이 문제인가 (공개·검증 가능)

AI-네이티브 조직에서 개발 지식이 **개인 세션에 갇혀** 팀으로 통합되지 않는다. 예전엔 코드리뷰·멘토링으로 퍼지던 시니어 판단이, 각자 사적인 AI 세션으로 일하면서 파편화된다.

이는 무신사 공개 자료로 두 갈래 모두 입증된다:

- **메커니즘 갭** — 무신사는 `AGENTS.md`로 규칙을 *"이후 생성하는 모든 코드에 적용"* 한다고 공개했다([Claude Code Agent Teams](https://techblog.musinsa.com/설-연휴에-claude-code-agent-teams를-데려갔습니다-fa96286f6954)). 하지만 이 규칙 파일은 **수동 관리**되고 한 사람의 교훈이 자동으로 들어가지 않는다.
- **교훈 갭** — 600줄 god-query, `DATE_FORMAT`의 인덱스 무력화(p99 17배), 타입 분기(OCP 위반), 리팩토링 전 Golden Master 누락, 단일계층 Redis 등 **비싸게 배운 교훈이 블로그 산문으로만** 존재한다(아래 출처). 새 에이전트는 이를 모른 채 같은 실수를 재생산한다.

> 무신사는 신입 채용 2차 면접에서 지원자에게 Codex를 주고 **자체 'AI 평가 툴'로 코드를 채점**한다([뉴스룸](https://newsroom.musinsa.com/newsroom-menu/2026-0205)). 이 플러그인은 그 "규칙 기반 AI 채점"을 *현직 개발자의 PR 시점*으로 옮긴 것이다.

## 3. 어떻게 작동하나 — 계층형(cascading) 룰북

플러그인 **코드는 고정**, **룰 데이터는 증식**한다. 룰은 위→아래로 합쳐 읽고, 아래 계층이 위를 덮어쓴다(같은 `id`):

```
1) seed   src/rules/seed.yaml          무신사 공개 교훈 (플러그인 동봉)      소유: 플러그인
2) org    .musinsa/org-source (선택)    조직 공통 룰 (여러 레포 공유)         소유: 조직
3) repo   .musinsa/rules.yaml           이 코드베이스의 팀 룰 (/remember)     소유: 팀
```

→ **추가 호스팅 주체가 필요 없다.** repo 룰북은 팀이 *이미 가진 레포*에 사는 파일이고, 공유는 평소의 git/PR 흐름 그대로다. 규칙도 코드처럼 PR 리뷰를 거쳐 품질이 유지된다.

### 캡처 → 강제 루프

```
[Dev A] /remember "결제 금액은 double 금지, BigDecimal 사용"
          → .musinsa/rules.yaml 에 구조화 규칙 append → PR → merge
[Dev B] 결제 코드에 double 사용 → /review
          → ❌ A의 규칙 위반: 금액은 BigDecimal (등록자 A) → 수정 제안
```

### 하이브리드 채점 (신뢰성)

- **결정론적 1차**: `src/scripts/check.py` 가 룰의 `detect.patterns`(정규식)로 재현 가능한 위반을 탐지 → 같은 diff엔 항상 같은 점수.
- **판단 2차**: 설계 냄새(Golden Master 누락 등)는 에이전트가 룰의 `llm_hint`로 판단.
- 점수: 100점 시작, `block` −15 / `warn` −8 / `info` −2, `block` 1개라도 있으면 게이트 **BLOCKED**.

## 4. 구조

```
src/
├── .codex-plugin/plugin.json     # 플러그인 매니페스트 (필수)
├── skills/
│   ├── review/SKILL.md           # 룰북 대비 변경분 검수 + 채점 (/review)
│   └── remember/SKILL.md         # 새 규칙 캡처 → 팀 룰북에 추가 (/remember)
├── rules/seed.yaml               # seed 계층: 무신사 공개 교훈 6종
└── scripts/check.py              # 결정론적 패턴 스캐너 (하이브리드 1차)
README.md
logs/                             # 제작 과정 AI 대화 로그 (편집 없음)
```

## 5. 사용법

```bash
# Codex 플러그인 설치 (마켓플레이스/로컬)
/plugins        # → 설치 후 활성화

# 규칙 추가 (버그 고친 뒤)
/remember "핫패스 목록 쿼리는 ID 먼저 조회 후 본문 hydrate"

# PR 전 검수
/review         # 변경분을 seed+repo 룰북으로 채점, 위반 위치·근거·수정·출처 출력
```

## 6. AI를 어떻게 활용했나

- 무신사 기술블로그 61개 글 + Codex/Claude 공개 사례를 다중 에이전트 리서치로 수집·구조화하여 seed 규칙의 근거(출처 URL·수치)를 확보.
- 각 규칙의 정규식/`llm_hint`/수정안 설계.
- 전 과정 AI 대화 로그는 `logs/` 에 편집 없이 보존.

## 7. 어떻게 검증했나

- `src/scripts/check.py` 를 합성 위반 코드(ORDER BY DATE_FORMAT, SELECT *, 4+ JOIN, 타입 if/else, RedisTemplate)로 실행해 **6개 seed 규칙이 모두 탐지**됨을 확인.
- 데모: 공개 Spring Boot 레포(`spring-petclinic`)에 안티패턴을 심고 `/review` before/after로 점수 변화 시연. (인프라 0)

## 8. 출처 (전부 공개·검증 가능)

| 규칙 | 출처 |
|---|---|
| 함수로 인한 인덱스 무력화 / covering index | [10초 타임아웃에서 벗어나기까지의 여정](https://techblog.musinsa.com/10초-타임아웃에서-벗어나기까지의-여정-a58eb8faca36) |
| 600줄 god-query 분해 | [600줄짜리 쿠폰 쿼리와의 아름다운 이별](https://medium.com/musinsa-tech/무신사-성장과-함께-거대해져온-600줄짜리-쿠폰-쿼리와의-아름다운-이별-e689d7d932b5) |
| 타입 분기 → 전략/팩토리(OCP) | [추상화 & 리팩토링을 통한 해외 물류사 개발 비용 절감](https://medium.com/musinsa-tech/추상화-리팩토링을-통한-해외-물류사-개발-비용-절감-c2bcc8d9624d) |
| 리팩토링 전 Golden Master | [리팩토링을 위한 통합 테스트](https://medium.com/musinsa-tech/리팩토링을-위한-통합-테스트-cd23498918a7) |
| 단일계층 Redis / 캐시 계층화 | [이구위크 전시 장애 대응기: Redis에는 무슨 일이](https://techblog.musinsa.com/이구위크-전시-장애-대응기-redis에는-무슨-일이-있었나-5599562d76b9) |
| AGENTS.md 규칙 주입 메커니즘 | [설 연휴에 Claude Code Agent Teams를 데려갔습니다](https://techblog.musinsa.com/설-연휴에-claude-code-agent-teams를-데려갔습니다-fa96286f6954) |
| AI 평가 툴 기반 코드 채점 | [무신사 뉴스룸 — AI 네이티브 채용](https://newsroom.musinsa.com/newsroom-menu/2026-0205) |
