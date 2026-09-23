# Launch drafts

Nothing here is posted automatically. Every item needs the author's go-ahead.

## Show HN

**Title:** Show HN: Jevcompat – a spec and conformance suite for the ~100 "Jev-compatible" servers

**Text:**

TypeSafe's Jev (System One) came out on Sept 15 with a closed model and a waitlisted API. Within
nine days about a hundred open-source servers claimed to be "Jev-compatible". I wanted to know what
that meant, and found there was nothing to check it against. TypeSafe's docs, its OpenAPI file and
its two SDKs disagree with each other in eight places (401 vs 403 for a missing key, whether
`instructions` is required, 2–10 score levels vs "at least one", …).

So I wrote the missing spec: 48 numbered requirements, each citing the official source it comes
from, with an appendix that resolves every disagreement by one rule. The rule: accept whatever any
official source says is valid, and produce only what every official client parses. Then I wrote a
suite that tests any server against the spec.

Results on the eight most-starred open servers:

- Two are conformant (kev and decider).
- Four can't take the documented 255 choice options. They stop at 26, 50, 64, or somewhere
  between 64 and 128.
- `confidence` is computed five different ways, so a 0.8 threshold means something different on
  each server.
- In one server, reordering the questions in a request moves an answer from 0.77 to 0.35.

Things I cared about, since this grades other people's work in public:

- Every check is proven to fail. A reference mock can break each requirement on purpose (47
  faults), and CI asserts that the targeted requirement fails and that no single fault smears
  across unrelated MUSTs.
- The semantic checks (does renaming a question id change the answer?) are statistics. They use
  repeated sends and a confirmation round, and are tested over many seeds for false positives
  against noisy and sampling servers.
- Every failure in the published results was checked by hand. Doing that found five bugs in the
  suite itself before publication.

There's also a proxy that puts a conformant API in front of a non-conformant server. It
recomputes what can be recomputed and refuses (502) what can't, rather than passing a wrong
answer through.

It doesn't test TypeSafe's hosted API: the suite sends malformed requests, and their terms
prohibit security testing. It isn't a benchmark; JevBench and sys1bench do accuracy and
calibration.

https://github.com/mandu5/jevcompat

**First comment (author):** a short note on the robustness rule and a link to SPEC Appendix A,
plus an invitation to open issues on any requirement people think is wrong.

## GeekNews (Show GN)

**제목:** jevcompat – "Jev 호환"이라고 주장하는 서버 ~100개를 위한 스펙과 적합성 테스트

**본문:**

TypeSafe가 9월 15일 Jev(System One)를 내놓았는데, 모델은 비공개였고 API는 대기열로만 열렸습니다.
그래서 9일 만에 "Jev 호환"을 내세운 오픈소스 서버가 100개 가까이 생겼습니다. 그런데 "호환"이 무슨 뜻인지
확인할 기준이 없었습니다. TypeSafe의 문서, OpenAPI 파일, 공식 SDK 두 개가 서로 여덟 군데에서 다르게
말합니다(키가 없을 때 401인지 403인지, `instructions`가 필수인지, score 레벨이 2–10개인지 1개 이상인지 등).

그래서 없던 스펙을 썼습니다. 요구사항 48개에 번호를 붙이고, 각각 근거가 되는 공식 출처를 달았습니다. 출처끼리
충돌하는 곳은 규칙 하나로 정했습니다. "공식 출처 중 하나라도 유효하다고 한 요청은 받고, 모든 공식
클라이언트가 파싱할 수 있는 응답만 낸다." 그리고 아무 서버나 이 스펙으로 검사하는 도구를 만들었습니다.

스타가 가장 많은 오픈 서버 8개를 측정한 결과입니다.
- 적합한 서버는 2개(kev, decider)입니다.
- 4개는 문서가 약속한 선택지 255개를 받지 못합니다. 26, 50, 64개, 또는 64~128개 사이에서 멈춥니다.
- `confidence` 계산 방식이 다섯 가지라서, 임계값 0.8이 서버마다 다른 뜻이 됩니다.
- 한 서버는 요청 안의 질문 순서만 바꿔도 답이 0.77에서 0.35로 바뀝니다.

남의 프로젝트를 공개적으로 채점하는 도구라 신경 쓴 점이 있습니다.
- 모든 검사가 실제로 실패할 수 있다는 걸 증명했습니다. 레퍼런스 서버에 요구사항마다 결함을 일부러
  주입할 수 있고(47종), 해당 요구사항만 실패하는지 CI에서 확인합니다.
- 질문 id를 바꾸면 답이 달라지는지 같은 의미 검사는 통계로 판정합니다(반복 전송 + 확인 라운드).
  노이즈가 있거나 샘플링하는 서버에 대해 여러 시드로 오탐률을 테스트했습니다.
- 공개한 실패는 전부 사람이 증거와 대조했습니다. 그 과정에서 도구 자체의 버그 5개를 찾아 공개 전에
  고쳤습니다.

맞지 않는 서버 앞에 두면 고칠 수 있는 건 고치고, 고칠 수 없는 건 틀린 답을 넘기는 대신 502로 거부하는
프록시도 들어 있습니다.

https://github.com/mandu5/jevcompat

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
