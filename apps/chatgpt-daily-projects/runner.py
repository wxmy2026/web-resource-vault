#!/usr/bin/env python3
"""Create one fresh ChatGPT conversation per job, inside the configured Project.

This deliberately uses the visible ChatGPT web UI rather than undocumented APIs.
A persistent Playwright profile keeps the login locally on this Mac.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent
CONFIG_PATH = ROOT / "config.json"
STATE_DIR = Path.home() / ".chatgpt-daily-projects"
STATE_PATH = STATE_DIR / "state.json"
LOG_PATH = STATE_DIR / "runner.log"
CHATGPT_URL = "https://chatgpt.com/"

PROMPT_SELECTORS = [
    "#prompt-textarea",
    '[data-testid="prompt-textarea"]',
    '[contenteditable="true"][role="textbox"]',
]
SEND_SELECTORS = [
    '[data-testid="send-button"]',
    "#composer-submit-button",
    'button[aria-label="Send prompt"]',
]


def log(message: str) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    line = f"{datetime.now().isoformat(timespec='seconds')} {message}"
    print(line, flush=True)
    with LOG_PATH.open("a", encoding="utf-8") as fh:
        fh.write(line + "\n")


def load_json(path: Path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def save_state(state: dict) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def visible_first(page, selectors, timeout_ms=15000):
    deadline = time.time() + timeout_ms / 1000
    while time.time() < deadline:
        for selector in selectors:
            loc = page.locator(selector)
            try:
                count = loc.count()
            except Exception:
                continue
            for i in range(min(count, 4)):
                item = loc.nth(i)
                try:
                    if item.is_visible():
                        return item
                except Exception:
                    pass
        page.wait_for_timeout(250)
    raise RuntimeError("Could not find ChatGPT prompt box. Login may have expired or the UI changed.")


def find_project_url(page, project_name: str) -> str:
    # ChatGPT Project links currently use /g/g-p-.../project.
    links = page.locator('a[href*="/g/g-p-"]')
    exact = None
    partial = None
    for i in range(links.count()):
        link = links.nth(i)
        try:
            text = (link.inner_text() or "").strip()
            href = link.get_attribute("href") or ""
        except Exception:
            continue
        if "/project" not in href:
            continue
        if text.casefold() == project_name.casefold():
            exact = href
            break
        if project_name.casefold() in text.casefold():
            partial = partial or href
    href = exact or partial
    if not href:
        raise RuntimeError(f'Project "{project_name}" was not found in the ChatGPT sidebar.')
    if href.startswith("http"):
        return href
    return "https://chatgpt.com" + href


def wait_until_done(page, timeout_ms=30 * 60 * 1000) -> None:
    deadline = time.time() + timeout_ms / 1000
    saw_assistant = False
    stable_text = ""
    stable_rounds = 0

    while time.time() < deadline:
        assistant = page.locator('[data-message-author-role="assistant"]')
        if assistant.count():
            saw_assistant = True
            last = assistant.last
            try:
                text = (last.inner_text() or "").strip()
            except Exception:
                text = ""
            if text and text == stable_text:
                stable_rounds += 1
            else:
                stable_text = text
                stable_rounds = 0

            # Copy-turn control normally appears after streaming completes.
            try:
                turn = page.locator('[data-testid^="conversation-turn-"]').last
                has_copy = turn.locator('[data-testid="copy-turn-action-button"]').count() > 0
            except Exception:
                has_copy = False

            if text and has_copy and stable_rounds >= 1:
                return
            # Fallback for UI variants without the copy button.
            if text and stable_rounds >= 4:
                send = page.locator('[data-testid="send-button"], #composer-submit-button')
                if send.count() and send.first.is_enabled():
                    return
        page.wait_for_timeout(2000)

    if saw_assistant:
        raise RuntimeError("Timed out while waiting for the response to finish.")
    raise RuntimeError("No assistant response appeared before timeout.")


def run_job(page, config: dict, job_name: str, job: dict, state: dict, force: bool) -> None:
    tz = ZoneInfo(config.get("timezone", "Asia/Shanghai"))
    today = datetime.now(tz).date().isoformat()
    state_key = f"{today}:{job_name}"
    if state.get("completed", {}).get(state_key) and not force:
        log(f"SKIP {job_name}: already completed for {today}")
        return

    page.goto(CHATGPT_URL, wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(3000)
    visible_first(page, PROMPT_SELECTORS, timeout_ms=20000)

    project_url = find_project_url(page, job["project"])
    log(f"OPEN {job_name}: {job['project']}")
    # Navigating to the Project URL itself starts from the Project composer,
    # rather than reusing yesterday's /c/... conversation.
    page.goto(project_url, wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(2000)

    prompt_path = ROOT / job["prompt_file"]
    prompt = prompt_path.read_text(encoding="utf-8").strip()
    date_title = f"{today}｜{job['title_prefix']}"
    prompt = f"本次独立聊天的章节标识：{date_title}\n\n{prompt}"

    box = visible_first(page, PROMPT_SELECTORS, timeout_ms=20000)
    box.fill(prompt)

    send = visible_first(page, SEND_SELECTORS, timeout_ms=10000)
    send.click()
    log(f"SENT {job_name}: waiting for completion")
    wait_until_done(page)

    final_url = page.url
    state.setdefault("completed", {})[state_key] = {
        "project": job["project"],
        "url": final_url,
        "finished_at": datetime.now(tz).isoformat(timespec="seconds"),
    }
    save_state(state)
    log(f"DONE {job_name}: {final_url}")


def login(config: dict) -> int:
    profile = Path(config["browser_profile"]).expanduser()
    profile.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            str(profile),
            headless=False,
            viewport={"width": 1280, "height": 900},
            args=["--disable-blink-features=AutomationControlled"],
        )
        page = context.pages[0] if context.pages else context.new_page()
        page.goto(CHATGPT_URL, wait_until="domcontentloaded", timeout=60000)
        log("LOGIN: sign in to ChatGPT in the opened browser. This profile stays local on the Mac.")
        try:
            visible_first(page, PROMPT_SELECTORS, timeout_ms=10 * 60 * 1000)
        except Exception as exc:
            log(f"LOGIN FAILED: {exc}")
            context.close()
            return 1
        log("LOGIN OK: ChatGPT composer detected. Closing setup browser.")
        context.close()
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--job", choices=["brief", "town", "all"], default="all")
    parser.add_argument("--login", action="store_true", help="Open the persistent browser profile for one-time sign-in")
    parser.add_argument("--force", action="store_true", help="Run even if this job already completed today")
    args = parser.parse_args()

    config = load_json(CONFIG_PATH, {})
    if not config:
        raise SystemExit("Missing config.json")
    if args.login:
        return login(config)

    state = load_json(STATE_PATH, {"completed": {}})
    profile = Path(config["browser_profile"]).expanduser()
    profile.mkdir(parents=True, exist_ok=True)

    names = list(config["jobs"].keys()) if args.job == "all" else [args.job]
    failures = 0

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            str(profile),
            headless=False,
            viewport={"width": 1280, "height": 900},
            args=["--disable-blink-features=AutomationControlled"],
        )
        page = context.pages[0] if context.pages else context.new_page()
        for name in names:
            try:
                run_job(page, config, name, config["jobs"][name], state, args.force)
            except (RuntimeError, PlaywrightTimeoutError, Exception) as exc:
                failures += 1
                log(f"ERROR {name}: {type(exc).__name__}: {exc}")
        context.close()

    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
