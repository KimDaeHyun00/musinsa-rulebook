# Demo — Musinsa Rulebook 시연 시나리오

가상의 "무신사 커머스 서비스" 레포(`demo/`)가 `musinsa-rulebook` 플러그인을 채택한 상태.
Codex 없이도 결정론적 엔진(`src/scripts/check.py`)으로 `/review`를 그대로 재현할 수 있다.
(실제 Codex에서는 `/review` 스킬이 아래 명령을 호출하고 `llm_hint` 판단을 더한다.)

## Scene 1 — PR 전 검수: 무신사 공개 교훈으로 BLOCKED

```bash
python3 src/scripts/check.py --report --rules src/rules/seed.yaml \
  --files demo/src/main/resources/mapper/CouponMapper.xml \
          demo/src/main/java/com/musinsa/demo/delivery/DeliveryTrackerService.java
```
→ **Score 53/100 · BLOCKED.** ORDER BY DATE_FORMAT(인덱스 무력화), SELECT *, 4+ JOIN god-query,
타입 if/else 분기, 단일계층 Redis — 각 위반에 위치·근거(수치)·수정·무신사 블로그 출처.

## Scene 2 — 캡처→강제 루프: 한 사람의 교훈이 모두에게

개발자 `donghyun`이 환불 금액 오차 인시던트 후 규칙을 등록한 상태(`demo/.musinsa/rules.yaml`).
이를 모르는 개발자 B의 결제 코드를 검수:

```bash
python3 src/scripts/check.py --report \
  --rules src/rules/seed.yaml --rules demo/.musinsa/rules.yaml \
  --files demo/src/main/java/com/musinsa/demo/payment/RefundService.java
```
→ **Score 85/100 · BLOCKED**, `rulebook: seed(6) + repo(1)`.
B의 코드가 **A(donghyun)의 규칙 `money-bigdecimal-not-double`** 으로 차단되고, 등록자까지 표시.
→ Codex에서는 `/remember "결제 금액은 double 금지, BigDecimal"` 한 줄이면 위 규칙이 자동 생성·append.

## Scene 3 — 수정 후 PASS

`double` → `BigDecimal` 로 고치면:
→ **Score 100/100 · PASS.** 게이트 통과.

## 핵심 메시지

- 점수는 **결정론적**(같은 diff = 같은 점수) → 심사관이 믿을 수 있다.
- 규칙은 **플러그인 재배포 없이** `.musinsa/rules.yaml`(=팀 레포의 파일)로 증식.
- seed 규칙은 전부 **공개·검증 가능한 무신사 출처**를 가진다.
