"""poke.py — 페이지의 «모든 조작»을 한 번씩 눌러 보고, 그 사이에 난 JS 오류·가로 넘침을 센다.

    python -X utf8 poke.py PAGE.html [--phone] [--shots DIR]

정지 화면 캡처는 «깨지는지»를 못 본다. 이 스크립트는 실제로 조작한다:
  · input[type=range]  → 최솟값, 최댓값, 원래 값 순서로 바꾸고 input 이벤트를 보낸다(끝까지 밀면 깨지는 코드가 여기서 드러난다)
  · .seg 버튼 · .btn · checkbox · select 의 모든 option → 하나씩 누른다
  · canvas → 가운데에서 오른쪽 아래로 끈다(끌기 핸들이 있으면 움직인다)
  · 퀴즈 .opt 는 누르지 않는다(누르면 정답이 고정된다 — 보는 사람 몫)
결과: 조작 수, pageerror·console.error 목록, 390px 폭에서의 가로 넘침 여부. 오류 0 이 통과다.
--shots DIR 을 주면 시뮬레이터마다 조작 뒤 화면을 PNG 로 남긴다 — 숫자가 «말이 되는지»는 그 그림을 눈으로 본다.
--full PAGE.png 는 페이지 전체 한 장(색 모드는 운영체제 설정을 따른다).

필요: pip install playwright && python -m playwright install chromium (또는 설치된 Chrome 을 channel="chrome" 으로 쓴다).
"""
import argparse, pathlib, sys


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("page")
    ap.add_argument("--phone", action="store_true", help="390px 폭으로 연다")
    ap.add_argument("--shots")
    ap.add_argument("--full", help="조작을 마친 뒤 페이지 전체를 이 PNG 로 남긴다")
    a = ap.parse_args()
    from playwright.sync_api import sync_playwright

    url = pathlib.Path(a.page).resolve().as_uri()
    errors, n = [], 0
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
        if a.full:
            pg.screenshot(path=a.full, full_page=True)
        br.close()

    print(f"조작 {n}회 · 오류 {len(errors)}건 · 가로 넘침 {max(0, over)}px ({vw}px 폭)")
    for e in errors[:30]:
        print("  ", e[:200])
    sys.exit(1 if errors or over > 0 else 0)


if __name__ == "__main__":
    main()
