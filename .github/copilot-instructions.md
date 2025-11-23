## Copilot instructions — juice-shop-testautomation

Summary
- This repository contains pytest-based UI + API tests written in Python using Selenium.
- Key parts: `tests/` (pytest tests), `pages/` (page objects), `tests/new-user.json` (test account), `tests/conftest.py` (fixtures), and `requirements.txt` (dependencies).

Big picture (how the pieces fit)
- Tests run with pytest and expect Juice Shop to be available at http://localhost:3000 (Docker). See `tests/conftest.py` for how the browser is created and how login is performed automatically before each test.
- UI tests drive Chrome via webdriver-manager (ChromeDriver is auto-downloaded). Page object helpers live under `pages/` (BasePage, HomePage, LoginPage, PaymentsPage).
- API tests reuse the browser session to extract auth tokens from `localStorage` and call backend endpoints (see `tests/test_api.py`). Endpoints or payload shapes may need adaptation to the Juice Shop version used.

How to run locally (developer workflow)
1. Ensure Docker and Docker Desktop are installed and running.
2. Start Juice Shop:
```bash
docker run -d -p 3000:3000 bkimminich/juice-shop
```
3. Create and activate a venv, install deps:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
4. Populate `tests/new-user.json` with the account you registered in the app (email/password).
5. Run tests:
```bash
# run all tests
pytest -q
# run a single test (useful during troubleshooting)
pytest tests/test_payments_ui.py::test_add_card_ui -q
```

Project-specific conventions & patterns
- Autouse login: `tests/conftest.py` registers an `autouse=True` fixture `login` that navigates to the app and logs in before every test. Tests assume the user exists in `tests/new-user.json`.
- WebDriver management: ChromeDriver is installed at runtime via `webdriver_manager.chrome.ChromeDriverManager()` inside `conftest.py`. If offline or behind a firewall, consider storing a local driver or using Selenium Manager.
- Page objects: `pages/` uses `BasePage` with an explicit `WebDriverWait` for stable interactions. Prefer adding stable locators (IDs, aria-labels) in `pages/` and call those from tests instead of raw XPath in tests.
- API tests: `tests/test_api.py` contains a helper that inspects `window.localStorage` to find auth tokens. Use browser DevTools (Network tab) to confirm the endpoint and payload shape if API calls fail.

Key files to look at when changing behavior
- `tests/conftest.py` — driver options (headless, window size), webdriver-manager usage, auto-login flow.
- `tests/new-user.json` — credentials used by tests; must match a manually created user in Juice Shop.
- `pages/*.py` — recommended place to change locators. Example stable locators:
  - `pages/login_page.py` uses IDs `email`, `password`, `loginButton`.
  - `pages/payments_page.py` expects `button#addNewCard`, `#cardNumber`, `#expiryMonth`, `#expiryYear`.

Selectors and flakiness
- Prefer IDs or aria-labels. If you change a locator, update the page object and all tests that reference it.
- If a locator is flaky, open http://localhost:3000 in Chrome, use DevTools to inspect the element, and paste the new stable selector into the corresponding `pages/*.py` locator.

Debugging tips specific to this repo
- If tests fail at browser startup: remove `opts.add_argument("--headless=new")` in `tests/conftest.py` to see browser activity and errors.
- If ChromeDriver errors occur on macOS M1/arm64, try running the container with `--platform linux/amd64` or ensure webdriver-manager downloads an M1-compatible driver.
- To inspect the exact API call/payload used by the UI, add a manual card via the UI while recording Network traffic in DevTools and mirror that endpoint/payload in `tests/test_api.py`.

What to avoid / expectations for AI edits
- Do not change the autouse login behavior lightly — many tests rely on it. If you need isolated tests, create a new fixture and mark tests explicitly.
- When updating locators, modify `pages/*.py` (single source of truth) and keep test assertions minimal.
- If adding new third-party dependencies, update `requirements.txt` and keep versions pinned (use the existing format).

If anything in this doc is unclear or you'd like different conventions (for example, switching to Selenium Manager or running tests inside Docker), tell me which change you prefer and I will update this file.

References
- `tests/conftest.py`, `tests/test_payments_ui.py`, `tests/test_api.py`, `pages/` and `requirements.txt`.
