import os
import asyncio
import re
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright, Page, TimeoutError as PlaywrightTimeout, Error as PlaywrightError
def read_links():
    links = []
    with open("links.txt", "r", encoding="utf-8") as f:
        for ln in f:
            s = ln.strip()
            if not s:
                continue
            links.append(s)
    return links


# --- читаем sessions.txt ---
def read_sessions():
    sessions = []
    with open("sessions.txt", "r", encoding="utf-8") as f:
        for ln in f:
            s = ln.strip()
            if not s:
                continue
            sessions.append(s)
    return sessions



async def main():
    sessions = read_sessions()
    links = read_links()

    if not sessions:
        print("[ERR] sessions.txt пустой или не найден")
        return
    if not links:
        print("[ERR] links.txt пустой или не найден")
        return
    async with async_playwright() as p:

        browser = await p.chromium.launch(headless=False)
        for session_name in sessions:
            state_file = f"states/{session_name}.json"
            if not os.path.exists(state_file):
                print(f"[WARN] state-файл не найден для {session_name}: {state_file} — пропускаю")
                continue

            print(f"\n============================")
            print(f"=== СЕССИЯ: {session_name} ===")
            print(f"=== STATE:  {state_file} ===")
            print(f"============================")

            context = await browser.new_context(storage_state=state_file)
            page = await context.new_page()

            await page.goto("https://web.max.ru/0")
            for link in links:
                await page.locator("//div[@placeholder='Сообщение']").first.fill(link)
                await page.keyboard.press("Enter")
                await page.locator(f"xpath=//a[@href='{link}']").first.click()
                await page.locator("xpath=( //button[@aria-label='🎉 УЧАСТВОВАТЬ 🎉'] )[last()]").click()
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await page.wait_for_timeout(1000)
                await page.locator("xpath=( //button[@aria-label='✅ Подписаться'] )[last()]").click()

                await page.wait_for_timeout(4000)
                text_content = await page.locator("xpath=(//div[contains(@class, 'bubble svelte-')]/span[contains(@class, 'text svelte-')])[last()]").inner_html()

                html = text_content
                print(html)
                soup = BeautifulSoup(html, "html.parser")

                statuses = []
                links = soup.find_all("a", class_="link")
                #links = soup.get_text(separator="\n").split("\n")
                for link in links:
                    status = None
                    for prev in link.previous_siblings:
                        if isinstance(prev, str):
                            text = prev.strip()
                            if "✅" in text:
                                status = "✅"
                                break
                            elif "⛔" in text:
                                status = "⛔"
                                break
                    statuses.append(status)
                print(statuses)



                links = soup.find_all("a", class_="link")
                hrefs = [link.get("href") for link in links]
                print(hrefs)

                result = list(zip(statuses, hrefs))
                print(result)

                only_cross = [tup for tup in result if tup[0] == '⛔']
                print(only_cross)

                for item in only_cross:
                    url = item[1]
                    await page.locator(f"xpath=//a[@href='{url}']").first.click()
                    target_button = page.locator("//button//span[text()='Принять'] | //button//span[text()='Подписаться']").first
                    await target_button.wait_for(state="visible", timeout=15000)
                    await target_button.click()
                    await page.locator(f"xpath=//button[@aria-label='Перейти назад']").first.click()

                await page.locator(f"xpath=(//button[@aria-label='❓ Проверить'])[last()]").first.click()
                await page.wait_for_timeout(4000)
                passed_content = page.locator("xpath=(//div[contains(@class, 'inlineKeyboard svelte-')])[last()]//button[@aria-label='🎉 Создать розыгрыш']")
                print("passed link")
                await page.goto("https://web.max.ru/0")   ################ ест и другие быстрые способы потом исправлю
            await context.close()
if __name__ == "__main__":
    asyncio.run(main())