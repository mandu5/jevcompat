---
id: "jevcompat-spec-for-jev-compatible-servers"
title: "[사이드 프로젝트] 'Jev 호환'이라는 말에 스펙이 없어서 — jevcompat을 만들며 배운 것"
titleEn: "[Side Project] 'Jev-compatible' had no spec — building jevcompat"
date: "2026-09-24"
excerpt: "TypeSafe의 Jev가 나오고 9일 만에 'Jev 호환' 오픈소스 서버가 100개 가까이 생겼는데, 무엇과 호환된다는 건지 확인할 기준이 없었다. 요구사항 48개짜리 스펙과 적합성 테스트를 만들어 스타가 가장 많은 서버 8개를 측정했다. 8개 중 적합한 건 2개였다. 만드는 동안 가장 어려웠던 건 기능이 아니라 남의 프로젝트를 틀리게 채점하지 않는 일이었다."
excerptEn: "Nine days after TypeSafe's Jev shipped, about a hundred open-source servers claimed to be 'Jev-compatible', with nothing to check the claim against. I wrote a 48-requirement spec and a conformance suite, and measured the eight most-starred servers: two conform. The hard part was not the checks; it was never grading someone else's project wrong."
slug: "jevcompat-spec-for-jev-compatible-servers"
image: "/images/jevcompat-cover.png"
tags:
  - "Open Source"
  - "Python"
  - "Side Project"
  - "API"
  - "Testing"
author:
  name: "Mandu"
  avatar: "/assets/images/avatar.jpg"
  followers: 1
---

## 무엇을 만들었나

[jevcompat](https://github.com/mandu5/jevcompat)은 세 가지로 되어 있다.

1. **SPEC.md**: TypeSafe System One API(`POST /v1/systemone`)가 지켜야 할 것을 번호 붙은 요구사항 48개로 정리한 비공식 스펙이다. 요구사항마다 MUST/SHOULD 수준과 근거 출처가 붙어 있다.
2. **`jevcompat test URL`**: 아무 서버에나 이 스펙을 돌린다. 실패하면 원인이 된 요청과 규칙을 어긴 응답 바이트를 같이 보여준다.
3. **`jevcompat proxy URL`**: 스펙을 안 지키는 서버 앞에 두면, 고칠 수 있는 건 고치고 고칠 수 없는 건 틀린 답을 넘기지 않고 거부한다.

## 왜 만들었나

9월 15일 TypeSafe가 Jev를 냈다. 타입이 있는 질문(예/아니오, 선택, 점수)을 넣으면 확률이 붙은 타입 있는 답을 돌려주는 모델이다. 모델은 비공개였고 API는 대기열로만 풀렸다. 그러자 "Jev 호환"을 내건 오픈소스 서버가 9일 만에 100개 가까이 생겼다.

실제로 스타가 많은 26개의 코드를 읽어봤다.

- `/v1/systemone`을 실제로 제공하는 건 14개뿐이었다.
- `confidence`의 뜻이 서버마다 달랐다. 최고 확률인 곳, 1·2위 차이인 곳, 1 − 엔트로피인 곳이 있었다.
- 선택지 상한이 26, 50, 64, 128개로 제각각이었다. 문서는 255개를 약속한다.
- 공식 SDK의 기본값인 `"model": "jev-latest"`를 받는 방식도 네 가지로 갈렸다.

"호환"이 무슨 뜻인지 확인할 기준이 없었다. 기준이 될 TypeSafe의 문서, OpenAPI 파일, SDK 두 개도 서로 여덟 군데에서 달랐다.

주변을 먼저 조사했다. 리더보드(JevBench), 캘리브레이션 벤치마크(sys1bench), semantic grep(17개), SQL 연동(25개)은 이미 있었다. 비어 있는 건 API 계약 자체였다. 마크다운이 구현체만 수십 개인 상태에서 CommonMark가 스펙과 테스트로 정리한 것과 같은 구도라고 봤다.

## 결과: 스타 상위 8개 서버

| 서버 | ★ | MUST | 판정 | Jev 클라이언트에서 깨지는 것 |
|---|---:|---:|---|---|
| kev (0.8B) | 5.8k | 32/32 | 적합 | — |
| decider (0.8B) | 338 | 32/32 | 적합 | — |
| von | 571 | 31/32 | 부적합 | 객체·배열 `instructions`를 거부 |
| rizzo-flow (1.7B) | 389 | 31/32 | 부적합 | 선택지 26개 초과를 거부 |
| Open-Jev (2B) | 284 | 31/32 | 부적합 | 한쪽만 있는 noul criteria를 거부 |
| laya | 20.1k | 30/32 | 부적합 | 선택지 128개를 거부, SDK가 못 읽는 `null` legend |
| jeff | 230 | 30/32 | 부적합 | 64개 초과를 거부, `score`가 자기 확률의 기댓값이 아님 |
| simple-jev (0.8B) | 499 | 29/32 | 부적합 | `jev-latest`를 거부, 50개 초과를 거부 |

8개 중 2개가 적합했다. 가장 눈에 띈 건 jeff였다. 요청 안의 질문 순서만 뒤집었는데 `team` 답이 Billing 0.768에서 0.351로 바뀌었다. 질문들이 인코더 패스 하나를 공유하기 때문이다.

## 가장 어려웠던 것: 남의 프로젝트를 틀리게 채점하지 않기

검사를 만드는 건 금방이었다. 그다음 일이 훨씬 오래 걸렸다. 이 도구는 남의 오픈소스를 공개적으로 채점한다. 그래서 가장 나쁜 버그는 기능 누락이 아니라 오탐, 즉 멀쩡한 서버에 "MUST 위반"을 붙이는 것이다.

그래서 세 겹으로 검증했다.

**1. 모든 검사는 실패할 수 있어야 한다.** 레퍼런스 서버(`jevcompat mock`)는 스펙을 정확히 구현하고, 요구사항마다 결함을 일부러 넣을 수 있다(47종). CI는 세 가지를 확인한다. 깨끗한 서버에서는 전부 통과하는지, 결함마다 해당 요구사항이 실패하는지, 결함 하나가 관계없는 MUST 여러 개로 번지지 않는지. 절대 실패하지 않는 검사는 없는 검사와 같다.

**2. 독립 리뷰를 세 번 받았다.** 첫 리뷰에서 치명적인 문제가 나왔다. "질문 id를 바꾸면 답이 달라지는가"를 요청 두 번의 차이로 판정했는데, 확률에 노이즈가 있는 정상 서버가 약 25% 확률로 떨어졌다. 테스트는 고정 시드 하나에서 우연히 통과하고 있었다. 지금은 요청을 여러 번 보내 평균을 비교하고, 합동 표준편차로 한계를 잡고, 새로 보낸 두 번째 라운드에서도 같은 방향으로 차이가 나야 실패로 친다. 오탐률은 여러 시드로 테스트한다. 그 밖에 이런 문제들이 있었다.
- 첫 요청에서 서버가 잠깐 502를 내면 "모델 이름을 안 받는다"로 오판했다.
- float32로 반올림한 값을 반올림으로 알아보지 못했다.
- 속도 제한(429)에 걸린 걸 서버 결함으로 셌다.

**3. 실서버 결과를 하나씩 사람이 봤다.** 8개 서버의 실패를 전부 요청·응답 증거와 대조했다. 여기서 도구 자체의 버그 5개가 더 나왔다.
- 구조화된 score 레벨을 문자열로 돌려주는 걸 위반으로 봤다. 그런데 API 문서는 legend 값을 문자열로 정의한다.
- 공식 문서의 예시를 모두 재현하는 confidence 공식이 두 개 있었는데, 하나만 인정하고 있었다.
- 새로 넣은 검사가 등록 순서 때문에 한 번도 실행되지 않았다.

전부 공개 전에 고쳤다. 최종 보고서에 남은 실패 42개는 모두 실제 위반이다([REVIEW.md](https://github.com/mandu5/jevcompat/blob/main/results/REVIEW.md)).

## 스펙을 쓸 때 정한 규칙 두 가지

- **MUST와 SHOULD는 규칙 하나로 나눈다.** 공식 문서나 SDK대로 짠 클라이언트가 깨지면(예외, 크래시, 맞는 척하는 틀린 답) MUST다. 공식 서버와 동작만 다르면 SHOULD다.
- **공식 출처끼리 충돌하면 견고성 규칙을 따른다.** 공식 출처 중 하나라도 유효하다고 한 요청은 받는다. 모든 공식 클라이언트가 파싱할 수 있는 응답만 낸다. 이 규칙 하나로 여덟 군데 충돌이 정리됐다.

## 하지 않은 것

- **정확도나 캘리브레이션 채점은 하지 않는다.** "똑똑한가"가 아니라 "내 클라이언트 코드가 돌아가는가"를 본다.
- **TypeSafe 호스티드 API는 테스트하지 않는다.** 도구가 일부러 잘못된 요청을 보내는데, TypeSafe 약관이 보안 테스트를 금지한다.

<!-- EN_START -->

## What I built

[jevcompat](https://github.com/mandu5/jevcompat) is three things:

1. **SPEC.md**: an unofficial, numbered spec of TypeSafe's System One API (`POST /v1/systemone`). It has 48 requirements, each with a level (MUST/SHOULD) and the official source it comes from.
2. **`jevcompat test URL`**: runs the spec against any server. Each failure comes with the request that caused it and the response bytes that broke the rule.
3. **`jevcompat proxy URL`**: sits in front of a non-conforming server, fixes what can be fixed, and refuses what can't instead of passing a wrong answer through.

## Why

TypeSafe released Jev on September 15. It takes typed questions (yes/no, choice, score) and returns typed answers with probabilities. The model was closed and the API waitlisted. Within nine days, about a hundred open-source servers called themselves "Jev-compatible".

I read the code of the 26 most-starred ones:

- Only 14 actually serve `/v1/systemone`.
- `confidence` meant different things on different servers: the top probability, the top-two margin, or 1 − entropy.
- The choice limit was 26, 50, 64 or 128. The docs promise 255.
- The official SDKs' default, `"model": "jev-latest"`, was handled four different ways.

There was nothing to check the claim against, and the would-be references — TypeSafe's docs, its OpenAPI file and its two SDKs — disagree in eight places.

I checked what already existed first. There were leaderboards (JevBench), calibration benchmarks (sys1bench), semantic grep tools (17) and SQL integrations (25). The empty slot was the API contract itself: the same situation Markdown was in before CommonMark gave dozens of implementations a spec and a test suite.

## Results: the eight most-starred servers

| server | ★ | MUST | verdict | what breaks for a Jev client |
|---|---:|---:|---|---|
| kev (0.8B) | 5.8k | 32/32 | conformant | — |
| decider (0.8B) | 338 | 32/32 | conformant | — |
| von | 571 | 31/32 | not conformant | object or array `instructions` rejected |
| rizzo-flow (1.7B) | 389 | 31/32 | not conformant | more than 26 options rejected |
| Open-Jev (2B) | 284 | 31/32 | not conformant | one-sided noul criteria rejected |
| laya | 20.1k | 30/32 | not conformant | 128 options rejected; a `null` legend value the SDK can't parse |
| jeff | 230 | 30/32 | not conformant | more than 64 options rejected; `score` isn't the expectation of its own probabilities |
| simple-jev (0.8B) | 499 | 29/32 | not conformant | `jev-latest` rejected; more than 50 options rejected |

Two of eight conform. The most striking finding was jeff: reversing the order of the questions in one request moved the `team` answer from Billing 0.768 to 0.351, because the questions share one encoder pass.

## The hard part: not grading anyone wrong

Writing the checks was quick. What came after took much longer. This tool grades other people's open-source work in public, so the worst bug isn't a missing feature. It's a false positive: a "MUST violation" stamped on a server that did nothing wrong.

So it was verified in three layers.

**1. Every check has to be able to fail.** The reference server (`jevcompat mock`) implements the spec exactly and can break any requirement on purpose (47 faults). CI checks three things: every check passes on the clean server, each fault fails its target requirement, and no single fault spreads into unrelated MUSTs. A check that can never fail is no check.

**2. Three independent reviews.** The first found a critical problem. "Does renaming a question id change the answer?" was judged from the difference between two requests, so correct servers with noisy probabilities failed about 25% of the time. The tests passed only because they used one lucky seed. Now requests are sent several times, means are compared against a limit from the pooled standard deviation, and a difference counts only if a fresh second round shows it in the same direction. The false-positive rate is tested over many seeds. The reviews also found:
- a 502 on the very first request, while the server warmed up, was blamed on the model name;
- float32-rounded values weren't recognised as rounded;
- rate limiting (429) was counted as a server defect.

**3. Every real failure checked by hand.** Each of the eight servers' failures was compared against the recorded request and response. That found five more bugs in the tool itself:
- a structured score level returned as a string was treated as a violation, although the API reference types legend values as strings;
- only one of the two confidence formulas that reproduce every documented example was accepted;
- a new check never ran, because of the order it was registered in.

All were fixed before publication. The 42 failures in the final reports are all real ([REVIEW.md](https://github.com/mandu5/jevcompat/blob/main/results/REVIEW.md)).

## Two rules for writing the spec

- **One rule sets the levels.** If a client written against the official docs or SDKs breaks (an exception, a crash, a wrong answer that looks right), it's a MUST. If the server only behaves differently from the official one, it's a SHOULD.
- **When official sources disagree, the robustness rule decides.** Accept any request that any official source calls valid. Produce only responses that every official client parses. That one rule settled all eight disagreements.

## What it doesn't do

- **It doesn't grade accuracy or calibration.** It asks "will my client code work?", not "is it smart?".
- **It doesn't test TypeSafe's hosted API.** The suite sends malformed requests on purpose, and TypeSafe's terms prohibit security testing.
