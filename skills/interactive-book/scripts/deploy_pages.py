"""deploy_pages.py — 정적 사이트 폴더를 GitHub Pages 로 올린다. «먼저 보여 주고, --yes 가 있어야 올린다.»

    python -X utf8 deploy_pages.py SITE_DIR REPO_NAME            # 점검만: 올라갈 파일·경고·주소를 보여 준다
    python -X utf8 deploy_pages.py SITE_DIR REPO_NAME --yes      # 실제로 만들고(없으면) push 하고 Pages 를 켠다

전제: `gh auth status` 가 로그인 상태. SITE_DIR 에 index.html 이 있어야 한다.
하는 일: SITE_DIR 를 git 저장소로(없으면 init) → .nojekyll → 커밋 → `gh repo create --public`(없을 때만) → push →
        Pages 를 main / (root) 로 켠다 → 빌드 끝날 때까지 기다려 주소를 찍는다.

⛔ Pages 는 «공개»다(무료 계정은 비공개 저장소의 Pages 를 못 쓴다). 그래서 점검 단계가 막는 것:
  · 강의안·교재 원본(.pdf .ppt .pptx .doc .docx .hwp .hwpx) — 저작권. 의대 강의안·족보는 공개 사이트에 올리지 않는다
  · 환자·지인 사진처럼 보이는 이미지는 사람이 확인(이미지 목록을 출력한다 — 출처·라이선스를 SOURCES 에 적었는지)
  · 50MB 넘는 파일(GitHub 거부)
  막힌 것이 있으면 --yes 여도 올리지 않는다. 일부러 올릴 것이면 --allow EXT 로 확장자를 풀어 준다.
⚠ 저장소 이름은 공개 URL 이 된다: https://<계정>.github.io/<REPO_NAME>/ — 영문 소문자·하이픈.
"""
import argparse, json, pathlib, subprocess, sys, time

BLOCK = {".pdf", ".ppt", ".pptx", ".doc", ".docx", ".hwp", ".hwpx", ".xls", ".xlsx"}
IMG = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".heic"}


def run(*cmd, cwd=None, check=True):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, encoding="utf-8")
    if check and r.returncode:
        sys.exit(f"실패: {' '.join(cmd)}\n{r.stdout}{r.stderr}")
    return r


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("site"); ap.add_argument("repo")
    ap.add_argument("--yes", action="store_true")
    ap.add_argument("--allow", action="append", default=[], help="막힌 확장자 하나를 푼다(예: --allow .pdf)")
    a = ap.parse_args()
    site = pathlib.Path(a.site).resolve()
    if not (site / "index.html").is_file():
        sys.exit(f"{site} 에 index.html 이 없다")
    who = run("gh", "api", "user", "-q", ".login", check=False)        # 파일 점검은 로그인 없이도 한다
    user = who.stdout.strip() if who.returncode == 0 else "<github 계정>"

    files = [p for p in site.rglob("*") if p.is_file() and ".git" not in p.parts]
    blocked = [p for p in files if p.suffix.lower() in BLOCK - set(a.allow)]
    big = [p for p in files if p.stat().st_size > 50 * 2**20]
    imgs = [p for p in files if p.suffix.lower() in IMG]
    print(f"올릴 폴더: {site}  ({len(files)}개, {sum(p.stat().st_size for p in files) / 2**20:.1f} MB)")
    print(f"공개 주소: https://{user}.github.io/{a.repo}/   저장소: https://github.com/{user}/{a.repo} (public)")
    for p in sorted(files)[:40]:
        print("  ", p.relative_to(site))
    if len(files) > 40:
        print(f"   … 외 {len(files) - 40}개")
    if imgs:
        print(f"[확인] 이미지 {len(imgs)}개 — 직접 만든 것인가, 출처·라이선스를 적었나, 사람 얼굴·환자 정보가 없나:")
        for p in imgs:
            print("    ", p.relative_to(site))
    for p in blocked:
        print(f"[막음] {p.relative_to(site)} — 원본 문서는 공개 사이트에 올리지 않는다(--allow {p.suffix.lower()} 로 풀 수 있다)")
    for p in big:
        print(f"[막음] {p.relative_to(site)} — 50MB 초과")
    if blocked or big:
        sys.exit("막힌 파일이 있어 멈춘다.")
    if not a.yes:
        print("\n점검만 했다. 위 목록이 맞으면 --yes 를 붙여 다시 실행한다.")
        return
    if who.returncode:
        sys.exit("gh 로그인이 필요하다: gh auth login")

    (site / ".nojekyll").touch()
    if not (site / ".git").exists():
        run("git", "init", "-b", "main", cwd=site)
    run("git", "add", "-A", cwd=site)
    if run("git", "diff", "--cached", "--quiet", cwd=site, check=False).returncode:
        run("git", "commit", "-m", "publish", cwd=site)
    exists = run("gh", "repo", "view", f"{user}/{a.repo}", check=False).returncode == 0
    if not exists:
        run("gh", "repo", "create", a.repo, "--public", "--source", str(site), "--remote", "origin", "--push", cwd=site)
    else:
        if run("git", "remote", cwd=site).stdout.strip() == "":
            run("git", "remote", "add", "origin", f"https://github.com/{user}/{a.repo}.git", cwd=site)
        run("git", "push", "-u", "origin", "main", cwd=site)
    if run("gh", "api", f"repos/{user}/{a.repo}/pages", check=False).returncode:
        run("gh", "api", "-X", "POST", f"repos/{user}/{a.repo}/pages",
            "-f", "build_type=legacy", "-f", "source[branch]=main", "-f", "source[path]=/")
    for _ in range(40):  # 최대 약 4분
        info = json.loads(run("gh", "api", f"repos/{user}/{a.repo}/pages").stdout)
        if info.get("status") == "built":
            print("배포 완료:", info.get("html_url")); return
        time.sleep(6)
    print("Pages 빌드가 아직 안 끝났다 — 몇 분 뒤 열어 본다:", f"https://{user}.github.io/{a.repo}/")


if __name__ == "__main__":
    main()
