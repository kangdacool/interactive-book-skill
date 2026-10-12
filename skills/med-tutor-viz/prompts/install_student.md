# 설치 — 과외 학생이 자기 Claude 에 med-tutor-viz 를 설치

저장소: https://github.com/kangdacool/interactive-book-skill (플러그인 `ibook`)
설치하면 호출 이름이 고정된다: **`/ibook:med-tutor-viz`**(과외용 빠른 한 장) · `/ibook:interactive-book`(천천히 깊게).

## A. Claude Code — 두 줄

Claude Code 입력창에 한 줄씩:

```
/plugin marketplace add kangdacool/interactive-book-skill
/plugin install ibook@kangdacool-ibook
```

갱신은 `/plugin marketplace update kangdacool-ibook`. 처음 한 번은 검사 도구용으로 아래 상자를 Claude Code 에 붙인다:

```text
ibook 플러그인을 방금 설치했어. 검사 도구가 돌게 준비해 줘.
1. 파이썬과 playwright 가 있는지 확인하고, 없으면 설치 명령을 보여 주고 내가 허락하면 설치해:
   pip install playwright  그리고  python -m playwright install chromium
2. 설치된 ibook 플러그인 폴더에서 skills/interactive-book/scripts/poke.py 를 같은 폴더의 assets/template.html 에 돌려
   「오류 0건」이 나오는지 보여 줘.
3. 끝나면 쓰는 법을 세 줄로: 강의안 PDF(+족보)를 주고 /ibook:med-tutor-viz 라고 하면 된다는 것.
설치 외에는 아무것도 바꾸지 마.
```

## B. claude.ai(웹·앱)만 쓰는 경우

1. 저장소의 **Releases** 에서 `med-tutor-viz.zip` 을 내려받는다(공유 폴더에도 같은 파일이 있다).
2. claude.ai → **Customize → Skills → 추가 → Skill 업로드** → 그 zip.
   스킬은 «코드 실행·파일 만들기» 기능이 켜져 있어야 돈다. 업로드 메뉴가 안 보이면 claude.ai 설정에서 그 기능부터 켠다.
3. 새 대화에서 강의안 PDF 를 첨부하고 「med-tutor-viz 로 이 강의 한 장 만들어줘」. 결과 HTML 을 내려받아 브라우저로 연다.
   (claude.ai 에서는 poke 검사가 안 돌 수 있다 — 그때는 슬라이더와 버튼을 직접 한 번씩 눌러 본다.)

## C. 둘 다 어렵다면

공유 폴더의 `빠른한장_프롬프트.md`(저장소에서는 `skills/med-tutor-viz/prompts/handout_tutor.md`) 상자를 복사해 Claude 에 붙이고 강의안을 첨부한다. 스킬 없이도 같은 규칙으로 만든다.
