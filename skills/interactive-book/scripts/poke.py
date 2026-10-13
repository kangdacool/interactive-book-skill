"""poke.py — 페이지의 «모든 조작»을 한 번씩 눌러 보고, 그 사이에 난 JS 오류·가로 넘침을 세고, «방향 검사»를 돌린다.

    python -X utf8 poke.py PAGE.html [--phone] [--shots DIR] [--full PNG] [--no-expect]

정지 화면 캡처는 «깨지는지»를 못 본다. 이 스크립트는 실제로 조작한다:
  · input[type=range]  → 최솟값, 최댓값, 원래 값 순서로 바꾸고 input 이벤트를 보낸다(끝까지 밀면 깨지는 코드가 여기서 드러난다)
  · .seg 버튼 · .btn · checkbox · select 의 모든 option → 하나씩 누른다
  · canvas → 가운데에서 오른쪽 아래로 끈다(끌기 핸들이 있으면 움직인다)
  · 퀴즈 .opt 는 누르지 않는다(누르면 정답이 고정된다 — 보는 사람 몫)
결과: 조작 수, pageerror·console.error 목록, 가로 넘침 여부. 오류 0 이 통과다.
--shots DIR 을 주면 시뮬레이터마다 조작 뒤 화면을 PNG 로 남긴다. --full PAGE.png 는 페이지 전체 한 장.

⭐ 방향 검사 — «오류 0» 은 «안 깨진다» 일 뿐, «맞다» 가 아니다.
첫 파일럿(2026-10-13)에서 poke 는 처음부터 0 이었는데 생리가 거꾸로 그려져 있었다(양압 흡기에 동맥압이 내려감).
그래서 페이지에 «이걸 이렇게 바꾸면 저 값은 이쪽으로 가야 한다» 를 «코드를 짜기 전에» 적고, 여기서 숫자로 확인한다.
페이지 안 <script type="application/json" id="expect"> 에 목록으로 둔다. 항목 하나:

  {"name": "용적↓ → PPV↑  (근거: 강의안 p.12)",       ← 실패 때 보이는 이름. 근거를 같이 적는다
   "sim": "sim-ppv",                                   ← 먼저 화면에 보이게 한다(K.loop 는 보일 때만 돈다)
   "before": [{"click": "#ppv-mode [data-value=ppv]"}],← 준비 조작(선택)
   "vary": {"set": "#ppv-v", "values": [5,4,3,2,1]},   ← 바꿔 가며 읽는다
   "wait": 5500,                                       ← 조작마다 기다린 뒤 읽는다(ms, 기본 150)
   "read": "#ppv-ppv",                                 ← 읽을 곳: 선택자(글의 첫 숫자) 또는 {"js": "식"}
   "trend": "up"}                                      ← up | down | same (같음: 모든 값이 같다)

  vary 꼴: {"set": 선택자, "values": [...]} · {"click": [선택자, ...]} · {"drag": 캔버스, "to": [[fx, fy], ...]}
           · {"wait": [ms, ...]}(시간이 지나며 읽기). 판정(여럿 가능): "trend" · "range": [lo, hi](null = 열림, 모든 읽기에)
           · "has": "글자"(모든 읽기의 글에 들어 있다).
  drag 는 K.drag 가 등록한 첫 핸들을 잡아 캔버스 비율 좌표(fx, fy; null = 그대로)로 옮긴다.
  {"js": "..."} 는 페이지가 K.probe 에 올린 모델 함수를 부른다 — 화면 숫자로 안 드러나는 «위상·방향» 을 묻는 자리다
  (예: K.probe.ppvInspMinusExp() > 0 — 흡기 박동의 수축기압이 호기보다 높다).
.sim 이 있는데 expect 가 없으면 실패한다(--no-expect 로 끈다). 하나라도 틀리면 실패다.
expect 는 «목록» 이어야 하고 항목마다 vary·read 가 있어야 한다 — 꼴이 틀리면 무엇이 틀렸는지 말하고 실패한다.
⛔ name 에 근거(쪽수·그림·표 번호: p.12 · pp.47–55 · 쪽 · Fig/그림 · Table/표 · Exhibit · 식)가 없으면 실패한다.
근거를 못 다는 방향은 시뮬레이터로 만들지 않는다(확인 목록으로 보낸다) — 2026-10-13 시험에서 근거 없는 방향 위에
시뮬레이터를 세운 페이지가 검사를 통과했다.
경고(실패 아님): 화면 글에 «» 가 6개 이상이면 센다(강조 부호 남발 — 같은 시험에서 한 페이지에 35개).

이 파일은 스킬 폴더 안에서 그대로 돌린다. 못 찾았다고 검사기를 새로 짜지 않는다 — 새로 짠 검사기는 이 검사들을 빠뜨린다.

필요: pip install playwright && python -m playwright install chromium (또는 설치된 Chrome 을 channel="chrome" 으로 쓴다).
"""
import argparse, json, pathlib, re, sys

NUM = re.compile(r"[-−]?\d+(?:\.\d+)?")
CITE = re.compile(r"pp?\.\s*\d|\d\s*쪽|fig(ure)?\.?\s*\d|그림\s*\d|table\s*\d|표\s*\d|exhibit\s*\d|식\s*\(?\d|eq\.?\s*\(?\d", re.I)
VARY_KEYS = ("set", "click", "drag", "wait")


def check_schema(checks):
    """expect 꼴 검사. 틀린 곳 목록을 돌려준다(빈 목록 = 통과)."""
    if not isinstance(checks, list):
        got = f"키 {sorted(checks)}" if isinstance(checks, dict) else type(checks).__name__
        return [f"expect 는 항목의 «목록» [ {{...}}, {{...}} ] 이어야 한다 — 받은 것: {got}. 머리말의 항목 꼴을 본다"]
    bad = []
    for i, c in enumerate(checks):
        tag = f"#{i + 1}"
        if not isinstance(c, dict):
            bad.append(f"{tag}: 항목이 객체가 아니다({type(c).__name__})"); continue
        tag += f" {c.get('name', '(이름 없음)')[:40]}"
        if "vary" not in c or not isinstance(c["vary"], dict) or not any(k in c["vary"] for k in VARY_KEYS):
            bad.append(f"{tag}: vary 가 없거나 꼴이 틀렸다(set·click·drag·wait 중 하나)")
        if "read" not in c:
            bad.append(f"{tag}: read 가 없다")
        if not any(k in c for k in ("trend", "range", "has")):
            bad.append(f"{tag}: 판정(trend·range·has)이 없다")
        if not CITE.search(c.get("name", "")):
            bad.append(f"{tag}: name 에 근거(쪽수·그림·표 번호)가 없다 — 못 달면 이 방향의 시뮬레이터를 빼고 확인 목록으로")
    return bad


def _num(text):
    m = NUM.search(text or "")
    return float(m.group().replace("−", "-")) if m else None


def _drag(pg, sel, to):
    # 캔버스를 화면 가운데로 — 위 끝에 두면 고정 머리띠가 핸들을 덮는다(2026-10-13 휴대폰 폭에서 실측)
    pg.locator(sel).evaluate("el => el.scrollIntoView({block: 'center'})"); pg.wait_for_timeout(100)
    box = pg.locator(sel).bounding_box()
    hd = pg.evaluate("s => { const c = document.querySelector(s); const h = c._handles && c._handles()[0]; return h ? [h.x, h.y] : null; }", sel)
    if not box or not hd:
        raise RuntimeError(f"{sel}: 끌 핸들이 없다(K.drag 로 등록했나)")
    x0, y0 = box["x"] + hd[0], box["y"] + hd[1]
    top = pg.evaluate("([x, y, s]) => { const e = document.elementFromPoint(x, y); return e === document.querySelector(s) ? null : (e ? e.tagName + '.' + e.className : 'none'); }", [x0, y0, sel])
    if top:
        raise RuntimeError(f"{sel}: 핸들 위를 다른 요소({top})가 덮고 있다 — 사람도 못 잡는다")
    x1 = x0 if to[0] is None else box["x"] + to[0] * box["width"]
    y1 = y0 if to[1] is None else box["y"] + to[1] * box["height"]
    pg.mouse.move(x0, y0); pg.mouse.down(); pg.mouse.move(x1, y1, steps=10); pg.mouse.up()


def _step(pg, s):
    if "click" in s:
        pg.click(s["click"])
    elif "set" in s:
        pg.locator(s["set"]).evaluate("(el, v) => { el.value = v; el.dispatchEvent(new Event('input', {bubbles: true})); "
                                      "el.dispatchEvent(new Event('change', {bubbles: true})); }", str(s["value"]))
    elif "drag" in s:
        _drag(pg, s["drag"], s["to"])
    if "wait" in s:
        pg.wait_for_timeout(s["wait"])


def _vary(v):
    if "set" in v:
        return [{"set": v["set"], "value": x} for x in v["values"]]
    if "click" in v:
        return [{"click": x} for x in v["click"]]
    if "drag" in v:
        return [{"drag": v["drag"], "to": t} for t in v["to"]]
    if "wait" in v:
        return [{"wait": w} for w in v["wait"]]
    raise ValueError(f"vary 꼴을 모른다: {v}")


def _read(pg, r):
    if isinstance(r, dict):
        x = pg.evaluate(f"() => ({r['js']})")
        return (float(x) if isinstance(x, (int, float)) else None), str(x)
    t = pg.inner_text(r)
    return _num(t), t


def run_expect(pg, url, checks):
    """방향 검사. 항목마다 새로 연 페이지에서 돈다(앞 검사의 상태가 섞이지 않게)."""
    fails = []
    for c in checks:
        name = c.get("name", "?")
        try:
            pg.goto(url, wait_until="load"); pg.wait_for_timeout(300)
            if c.get("sim"):
                pg.locator("#" + c["sim"]).scroll_into_view_if_needed()
            for s in c.get("before", []):
                _step(pg, s); pg.wait_for_timeout(100)
            vals, texts = [], []
            for s in _vary(c["vary"]):
                _step(pg, s); pg.wait_for_timeout(c.get("wait", 150))
                v, t = _read(pg, c["read"]); vals.append(v); texts.append(t)
        except Exception as e:
            fails.append(f"{name}: 실행 실패 — {str(e)[:160]}"); continue
        why = []
        nums = [v for v in vals if v is not None]
        tr = c.get("trend")
        if tr and len(nums) != len(vals):
            why.append("숫자를 못 읽은 값이 있다")
        elif tr == "up" and not (all(b >= a for a, b in zip(nums, nums[1:])) and nums[-1] > nums[0]):
            why.append("오르지 않는다")
        elif tr == "down" and not (all(b <= a for a, b in zip(nums, nums[1:])) and nums[-1] < nums[0]):
            why.append("내려가지 않는다")
        elif tr == "same" and len(set(nums)) > 1:
            why.append("같지 않다")
        if "range" in c:
            lo, hi = c["range"]
            if any(v is None or (lo is not None and v < lo) or (hi is not None and v > hi) for v in vals):
                why.append(f"범위 [{lo}, {hi}] 밖")
        if "has" in c and not all(c["has"] in t for t in texts):
            why.append(f"«{c['has']}» 없음")
        shown = " → ".join(t.strip()[:24] for t in texts)
        print(("  ✗ " if why else "  ✓ ") + f"{name}   [{shown}]" + (f"   ← {', '.join(why)}" if why else ""))
        if why:
            fails.append(f"{name}: {', '.join(why)}")
    return fails


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("page")
    ap.add_argument("--phone", action="store_true", help="390px 폭으로 연다")
    ap.add_argument("--shots")
    ap.add_argument("--full", help="조작을 마친 뒤 페이지 전체를 이 PNG 로 남긴다")
    ap.add_argument("--no-expect", action="store_true", help="방향 검사를 건너뛴다(시뮬레이터 없는 페이지만)")
    a = ap.parse_args()
    from playwright.sync_api import sync_playwright

    url = pathlib.Path(a.page).resolve().as_uri()
    errors, n, efails = [], 0, []
    with sync_playwright() as p:
        try:
            br = p.chromium.launch(channel="chrome", args=["--use-angle=swiftshader", "--enable-unsafe-swiftshader"])
        except Exception:
            br = p.chromium.launch(args=["--use-angle=swiftshader", "--enable-unsafe-swiftshader"])
        vw = 390 if a.phone else 1280
        pg = br.new_page(viewport={"width": vw, "height": 900})
        pg.on("pageerror", lambda e: errors.append(f"pageerror: {e}"))
        pg.on("console", lambda m: errors.append(f"console.{m.type}: {m.text}") if m.type == "error" else None)
        pg.goto(url, wait_until="load")
        pg.wait_for_timeout(800)

        # 1. 방향 검사
        raw = pg.evaluate("() => { const e = document.getElementById('expect'); return e ? e.textContent : null; }")
        has_sim = pg.evaluate("() => document.querySelectorAll('.sim').length")
        if a.no_expect:
            pass
        elif raw is None:
            if has_sim:
                efails.append("방향 검사(<script type=application/json id=expect>)가 없다 — 시뮬레이터마다 «바꾸면 어느 쪽으로»를 적는다")
        else:
            try:
                checks = json.loads(raw)
            except json.JSONDecodeError as e:
                checks, efails = None, [f"expect 가 JSON 이 아니다: {e}"]
            if checks is not None:
                efails = check_schema(checks)
                if efails:
                    print("방향 검사 꼴이 틀렸다 — 돌리지 않았다")
                else:
                    print(f"방향 검사 {len(checks)}개")
                    efails = run_expect(pg, url, checks)
                    pg.goto(url, wait_until="load"); pg.wait_for_timeout(500)

        # 2. 모든 조작
        for i, sim in enumerate(pg.query_selector_all(".sim")):
            sid = sim.get_attribute("id") or f"sim{i}"
            sim.scroll_into_view_if_needed()
            for r in sim.query_selector_all("input[type=range]"):
                orig = r.input_value()
                for v in (r.get_attribute("min") or "0", r.get_attribute("max") or "100", orig):
                    r.evaluate("(el, v) => { el.value = v; el.dispatchEvent(new Event('input', {bubbles: true})); "
                               "el.dispatchEvent(new Event('change', {bubbles: true})); }", v)
                    n += 1
            for b in sim.query_selector_all(".seg button, .btn, button:not(.opt)"):
                if b.is_visible():
                    b.click(); n += 1; pg.wait_for_timeout(60)
            for c in sim.query_selector_all("input[type=checkbox]"):
                c.click(); c.click(); n += 2
            for s in sim.query_selector_all("select"):
                for o in s.query_selector_all("option"):
                    s.select_option(o.get_attribute("value")); n += 1
            for cv in sim.query_selector_all("canvas"):
                bb = cv.bounding_box()
                if bb and bb["width"] > 0:
                    pg.mouse.move(bb["x"] + bb["width"] / 2, bb["y"] + bb["height"] / 2)
                    pg.mouse.down(); pg.mouse.move(bb["x"] + bb["width"] * 0.9, bb["y"] + bb["height"] * 0.8, steps=8)
                    pg.mouse.up(); n += 1
            pg.wait_for_timeout(150)
            if a.shots:
                pathlib.Path(a.shots).mkdir(parents=True, exist_ok=True)
                sim.screenshot(path=str(pathlib.Path(a.shots) / f"{sid}.png"))

        over = pg.evaluate("() => document.documentElement.scrollWidth - window.innerWidth")
        guil = pg.evaluate("() => (document.body.innerText.match(/«/g) || []).length")
        if a.full:
            pg.screenshot(path=a.full, full_page=True)
        br.close()

    print(f"조작 {n}회 · 오류 {len(errors)}건 · 가로 넘침 {max(0, over)}px ({vw}px 폭) · 방향 검사 실패 {len(efails)}건")
    for e in errors[:30]:
        print("  ", e[:200])
    for e in efails:
        print("   방향:", e)
    if guil >= 6:
        print(f"   [경고] 화면 글에 «» {guil}쌍 — 강조 부호를 거의 다 뺀다(실패는 아님)")
    sys.exit(1 if errors or over > 0 or efails else 0)


if __name__ == "__main__":
    main()
