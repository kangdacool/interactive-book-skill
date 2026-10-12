"""package_for_student.py — 과외 학생에게 줄 med-tutor-viz 꾸러미를 만든다(혼자서 도는 사본).

    python -X utf8 package_for_student.py OUT_DIR

만드는 것(OUT_DIR):
  med-tutor-viz/            ← Claude Code 용: 통째로 ~/.claude/skills/ 에 복사
      SKILL.md  assets/template.html  scripts/poke.py  prompts/handout_tutor.md
  med-tutor-viz.zip         ← claude.ai 「Skill 업로드」용(같은 내용, 최상위 폴더 하나)
  설치_프롬프트.md          ← 학생이 Claude Code 에 붙일 설치 문구(install_student.md)
  빠른한장_프롬프트.md      ← 스킬 없이 쓰는 문구(handout_tutor.md)

정본은 스킬 폴더(skills/)다. template·poke 는 interactive-book 의 것을 «복사»해 넣는다 — 학생 컴퓨터에는
interactive-book 이 없다. 정본을 고쳤으면 이 스크립트를 다시 돌려 꾸러미를 새로 만든다(손으로 고치지 않는다).
연구실 경로·이름이 꾸러미에 섞이지 않았는지 마지막에 검사한다.
"""
import pathlib, re, shutil, sys, zipfile

HERE = pathlib.Path(__file__).resolve().parents[1]          # skills/med-tutor-viz
BOOK = HERE.parent / "interactive-book"
LEAK = re.compile(r"[A-Z]:\\\\?Onedrive|claude-config|agent/tools|연구자", re.I)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    out = pathlib.Path(sys.argv[1]).resolve()
    pkg = out / "med-tutor-viz"
    if pkg.exists():
        shutil.rmtree(pkg)
    (pkg / "assets").mkdir(parents=True); (pkg / "scripts").mkdir(); (pkg / "prompts").mkdir()
    shutil.copy2(HERE / "SKILL.md", pkg / "SKILL.md")
    shutil.copy2(BOOK / "assets" / "template.html", pkg / "assets" / "template.html")
    shutil.copy2(BOOK / "scripts" / "poke.py", pkg / "scripts" / "poke.py")
    shutil.copy2(HERE / "prompts" / "handout_tutor.md", pkg / "prompts" / "handout_tutor.md")
    shutil.copy2(HERE / "prompts" / "install_student.md", out / "설치_프롬프트.md")
    shutil.copy2(HERE / "prompts" / "handout_tutor.md", out / "빠른한장_프롬프트.md")

    zp = out / "med-tutor-viz.zip"
    with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(pkg.rglob("*")):
            if f.is_file():
                z.write(f, f.relative_to(out).as_posix())

    leaks = []
    for f in list(pkg.rglob("*")) + [out / "설치_프롬프트.md", out / "빠른한장_프롬프트.md"]:
        if f.is_file():
            for i, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
                if LEAK.search(line):
                    leaks.append(f"{f.relative_to(out)}:{i}: {line.strip()[:100]}")
    print(f"꾸러미: {out}")
    for f in sorted(out.rglob("*")):
        if f.is_file():
            print("  ", f.relative_to(out))
    if leaks:
        print("[확인] 연구실 경로·이름으로 보이는 줄:")
        for l in leaks:
            print("   ", l)
        sys.exit(1)
    print("누출 검사 통과")


if __name__ == "__main__":
    main()
