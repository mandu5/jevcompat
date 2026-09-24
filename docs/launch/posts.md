# Launch drafts

Nothing here is posted automatically. Every item needs the author's go-ahead.

## Show HN

**Title:** Show HN: Jevcompat – "Jev-compatible" servers disagree on what confidence means

**URL:** https://github.com/mandu5/jevcompat

**Text:**

Jev (TypeSafe's typed-decision model) is sold on calibrated confidence: pick a threshold,
automate what clears it, and send the rest to a person. Nine days after launch there are about a
hundred open "Jev-compatible" servers, so I wrote the API contract down as a spec (48
requirements, each citing TypeSafe's docs, OpenAPI file or SDKs) and a suite that checks any
server against it.

The finding I didn't expect: the servers compute `confidence` four different ways (TypeSafe's
formula, the top probability, the top-two margin, 1 − entropy). On the same 204 answers, a 0.9
threshold auto-accepts 58% under TypeSafe's formula and 30% under the most-starred clone's. So
code tuned against Jev silently changes its automation rate when you point it at a clone.

Of the eight most-starred servers, two pass every MUST. The others cap choices at 26, 50 or 64
options (the docs say 255), reject the SDK's default model name, or return a `score` that isn't
the expectation of their own probabilities. In one server, reordering questions in a request
flips an answer from 0.77 to 0.35.

Because it grades other people's projects in public, every check is proven able to fail (a
reference server breaks each requirement on purpose), the statistical checks are tested for
false positives over many seeds, and every failure was checked by hand. That found five bugs in
my own suite before publishing. There's also a proxy that recomputes what can be recomputed
and refuses, with a 502, what can't.

It doesn't test TypeSafe's hosted API. The suite sends malformed requests on purpose, and their
terms prohibit security testing.

**When:** a US weekday morning (Tue–Thu, 8–10am ET = 21–23 KST).

## GeekNews (Show GN)

**제목:** jevcompat – "Jev 호환" 서버 8개 측정: 같은 답, 같은 임계값 0.9인데 자동 승인률 30%~63%

**URL:** https://github.com/mandu5/jevcompat

**본문:**

Jev(TypeSafe의 타입 있는 결정 모델)의 핵심은 보정된 confidence입니다. 임계값을 정해 두고, 넘는 답은
자동 처리하고, 넘지 못한 답은 사람에게 넘깁니다. 출시 9일 만에 "Jev 호환" 오픈소스 서버가 100개 가까이
생겨서, API 계약을 요구사항 48개짜리 스펙으로 쓰고(각 요구사항에 TypeSafe 문서·OpenAPI·SDK 출처 표기)
아무 서버나 검사하는 도구를 만들었습니다.

예상하지 못한 발견이 있었습니다. 서버마다 `confidence`를 네 가지 방식으로 계산합니다(TypeSafe 공식,
최고 확률, 1·2위 차이, 1 − 엔트로피). 같은 답 204개에 임계값 0.9를 적용하면 TypeSafe 공식으로는 58%가
자동 승인되는데, 스타가 가장 많은 클론의 방식으로는 30%만 승인됩니다. Jev에 맞춰 튜닝한 코드를 클론으로
옮기면 자동화율이 조용히 절반이 됩니다.

스타 상위 8개 중 필수(MUST) 요구사항을 모두 지킨 서버는 2개입니다. 나머지는 이런 문제가 있습니다.
- 선택지를 26·50·64개에서 막습니다(문서는 255개).
- SDK의 기본 모델 이름을 거부합니다.
- `score`가 자기 확률의 기댓값이 아닙니다.
- 한 서버는 질문 순서만 바꿔도 답이 0.77에서 0.35로 뒤집힙니다.

남의 프로젝트를 공개로 채점하는 도구라 오탐을 가장 경계했습니다.
- 모든 검사가 실제로 실패할 수 있다는 걸 결함 주입으로 증명했습니다.
- 통계 검사는 여러 시드로 오탐률을 테스트했습니다.
- 공개한 실패는 전부 사람이 증거와 대조했습니다. 그 과정에서 제 도구의 버그 5개를 먼저 고쳤습니다.

## awesome-jev entry (Evaluation / Benchmarking)

```
- [jevcompat](https://github.com/mandu5/jevcompat) — A testable spec (48 requirements, each citing TypeSafe's docs, OpenAPI file or SDKs) and conformance suite for Jev-compatible servers, with a normalising proxy and a GitHub Action. Results for the eight most-starred open servers included.
```

## Replica maintainers

Open at most one issue per repository, only with the author's go-ahead, and only after the
repository is public. Lead with what works. Link the report. Offer the Action; never demand a fix.

**To a conformant server (kev, decider):**

> Title: kev passes every MUST in the jevcompat spec
>
> Hi! I wrote a spec and conformance suite for Jev-compatible servers
> (https://github.com/mandu5/jevcompat). kev 0.8B passes all 32 applicable MUSTs, one of two among
> the eight most-starred servers. The full report is here: <link>. If you'd like the badge in your
> README, the snippet is at the top of the report. There's also a GitHub Action if you want to keep
> it green in CI. The two SHOULD notes are listed in the report; they're conventions, not bugs.

**To a server with MUST failures:**

> Title: jevcompat report: <n> MUST findings (e.g. 128-option choices get 422)
>
> Hi! I wrote a spec and conformance suite for Jev-compatible servers
> (https://github.com/mandu5/jevcompat) and ran it against <repo>@<sha> on an M1 Pro. The report,
> with the exact request and response for each finding, is here: <link>.
>
> <One or two sentences on the MUST findings, quoting the evidence.>
>
> Each requirement links to the official source it comes from. If you think one is wrong, I'd
> genuinely like an issue on jevcompat. The spec is a draft and the point is to get it right.
