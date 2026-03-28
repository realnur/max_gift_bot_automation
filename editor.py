import os
from playwright.sync_api import sync_playwright

profile = input("Введите название сессии: ")
os.makedirs("states", exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://web.max.ru/")
    input("Войдите и нажмите Enter в консоли...")

    context.storage_state(path=f"states/{profile}.json")
    print(f"Состояние сохранено в states/{profile}.json")
    browser.close()


with open(f"sessions.txt", "r", encoding="utf-8") as f:
    lines = f.readlines()
clean_lines = [" ".join(line.strip().split()) for line in lines if line.strip()]
with open(f"sessions.txt", "w", encoding="utf-8") as f:
    for line in clean_lines:
        f.write(line + "\n")
with open(f"sessions.txt", "a", encoding="utf-8") as f:
    f.write(profile + "\n")