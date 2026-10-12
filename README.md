# interactive-book-skill

만져 보며 배우는 웹 페이지를 만드는 Claude 스킬 둘.

| 호출 | 용도 | 속도 |
|---|---|---|
| `/ibook:interactive-book` | 한 주제를 장(章) 단위 인터랙티브 교과서로 만들어 GitHub Pages 로 배포. 나 자신이 제대로 이해하거나 옆사람에게 건넬 때 | 느리게, 정확하게 — 목차 승인 → 1장 → 나머지 |
| `/ibook:med-tutor-viz` | 의대 강의 하나를 시험 축만 골라 «빠른 한 장»으로. 블록제 본과생용 | 강의 하나에 40분 안. 공개 배포하지 않음 |

둘이 같은 템플릿(`skills/interactive-book/assets/template.html`)과 검사 도구를 쓴다.

- **`poke.py`** — 페이지의 모든 슬라이더를 최소·최대로 밀고, 버튼·선택·캔버스 끌기를 한 번씩 해서 JS 오류와 휴대폰 폭 가로 넘침을 센다. 오류 0이 통과다.
- **`deploy_pages.py`** — 기본은 점검만 한다. `--yes`가 있어야 GitHub Pages(공개)로 올린다. 강의안·교재 원본 문서(.pdf .pptx .docx .hwpx)가 섞여 있으면 막는다.

## 설치

**Claude Code — 플러그인**

```
/plugin marketplace add kangdacool/interactive-book-skill
/plugin install ibook@kangdacool-ibook
```

갱신: `/plugin marketplace update kangdacool-ibook`. 검사 도구에는 `pip install playwright` 와 `python -m playwright install chromium` 이 필요하다.

**claude.ai** — [Releases](https://github.com/kangdacool/interactive-book-skill/releases) 의 `interactive-book.zip` · `med-tutor-viz.zip` 을
Customize → Skills → Skill 업로드.

**스킬 없이** — 붙여 쓰는 프롬프트:
[공부·전달용](skills/interactive-book/prompts/handout_study.md) ·
[의대 빠른 한 장](skills/med-tutor-viz/prompts/handout_tutor.md) ·
[학생 설치 안내](skills/med-tutor-viz/prompts/install_student.md)

## 원칙(요약)

- 질문 하나에 시뮬레이터 하나, 컨트롤 1~4개. 값을 끝까지 밀면 무너지는 모습이 보이게.
- 숫자는 전부 출처와 짝지어 둔다. 의대 과외용은 그 학교 강의안이 정답 기준이다.
- 짧은 평서문. 수사형 제목·「A가 아니라 B」 같은 말버릇을 쓰지 않는다.
- 다크 모드, 휴대폰 390px 에서 넘침 없음. 만든 뒤 `poke.py` 오류 0.

## 배운 곳

구성 원칙은 [Books · 인터랙티브 교과서 시리즈](https://books.euiyun.com/)의 공개 작성 가이드
(예: [BodyBook CONTRIBUTING](https://github.com/geniuskey/bodybook/blob/main/CONTRIBUTING.md), 코드 MIT · 콘텐츠 CC BY 4.0)에서 배웠다.
이 저장소의 코드와 글은 새로 썼고, 그 시리즈의 글·그림을 포함하지 않는다.

## 라이선스

MIT
