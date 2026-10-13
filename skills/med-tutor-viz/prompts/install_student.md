# 설치 — 과외 학생이 자기 Claude 에 med-tutor-viz 를 설치

저장소: https://github.com/kangdacool/interactive-book-skill (플러그인 `ibook`)
설치하면 호출 이름이 고정된다: **`/ibook:med-tutor-viz`**(과외용 빠른 한 장) · `/ibook:interactive-book`(천천히 깊게).

## A. Claude 데스크톱 앱(Code) — 상자 하나

데스크톱 앱에서는 `/plugin` 이 명령으로 실행되지 않고 플러그인 창을 연다. 그 창의 「마켓플레이스 추가 → 저장소에서 추가」는
Mac 에서 「마켓플레이스 추가에 실패했습니다」가 난 적이 있다(2026-10-14). 그래서 설치를 Claude 에게 맡긴다.

1. Claude 앱 → Code → 새 세션(폴더는 아무거나).
2. 아래 상자를 붙여 넣고 Enter. 묻는 것은 전부 허락. Mac 에서 「명령어 라인 개발자 도구」 설치 창이 뜨면 설치.

```text
ibook 플러그인을 설치하고 바로 쓸 수 있게 준비해 줘. 나는 허락만 누를게.
1. 터미널 명령으로 설치해:
   claude plugin marketplace add kangdacool/interactive-book-skill
   claude plugin install ibook@kangdacool-ibook
   - claude 명령을 못 찾으면 이 앱이 쓰는 claude 실행 파일 위치를 찾아 그걸로 실행해.
   - git 이 없어서 실패하면 설치를 안내하고(Mac: xcode-select --install), 내가 끝났다고 하면 다시 시도해.
2. 파이썬과 playwright 가 없으면 설치해:
   pip install playwright  그리고  python -m playwright install chromium
3. 설치된 ibook 플러그인 폴더에서 skills/interactive-book/scripts/poke.py 를 같은 폴더의 assets/template.html 에 돌려
   「오류 0건」이 나오는지 보여 줘.
4. 막힌 곳이 있으면 무엇 때문인지 한 줄로 말해 줘.
설치 외에는 아무것도 바꾸지 마.
```

3. 앱을 완전히 종료(Mac ⌘Q)했다가 다시 열고, 입력창에 `/ibook` 을 쳐서 `ibook:med-tutor-viz` 가 뜨는지 본다.

**터미널판 Claude Code** 는 `/plugin` 이 바로 실행된다: `/plugin marketplace add kangdacool/interactive-book-skill` →
`/plugin install ibook@kangdacool-ibook` → `/reload-plugins` → 위 상자(1번은 이미 됐다고 답한다).
갱신은 `claude plugin marketplace update kangdacool-ibook` 와 `claude plugin update ibook@kangdacool-ibook`.

## B. claude.ai(웹·앱)만 쓰는 경우

1. 저장소의 **Releases** 에서 `med-tutor-viz.zip` 을 내려받는다(공유 폴더에도 같은 파일이 있다).
2. claude.ai → **Customize → Skills → 추가 → Skill 업로드** → 그 zip.
   스킬은 «코드 실행·파일 만들기» 기능이 켜져 있어야 돈다. 업로드 메뉴가 안 보이면 claude.ai 설정에서 그 기능부터 켠다.
3. 새 대화에서 강의안 PDF 를 첨부하고 「med-tutor-viz 로 이 강의 한 장 만들어줘」. 결과 HTML 을 내려받아 브라우저로 연다.
   (claude.ai 에서는 poke 검사가 안 돌 수 있다 — 그때는 슬라이더와 버튼을 직접 한 번씩 눌러 본다.)

## C. 둘 다 어렵다면

공유 폴더의 `빠른한장_프롬프트.md`(저장소에서는 `skills/med-tutor-viz/prompts/handout_tutor.md`) 상자를 복사해 Claude 에 붙이고 강의안을 첨부한다. 스킬 없이도 같은 규칙으로 만든다.
