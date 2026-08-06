import asyncio
import os
import hashlib
import requests
from playwright.async_api import async_playwright

from config import DOCTORS, CHECK_INTERVAL


TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


last_status = {}


def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    }

    try:
        requests.post(url, data=data, timeout=20)
    except Exception as e:
        print("Telegram error:", e)


async def check_doctor(page, doctor):
    doctor_name = doctor["name"]
    doctor_id = doctor["id"]

    url = (
        "https://nobat.dums.ac.ir/"
        f"ShafaSchedule/schedule-doctor-program?drCode={doctor_id}"
    )

    await page.goto(url, wait_until="networkidle", timeout=60000)

    await page.wait_for_timeout(5000)

    content = await page.text_content("body")

    if not content:
        return

    # حذف فاصله‌های اضافی
    content = " ".join(content.split())

    # تشخیص تغییر وضعیت صفحه
    status_hash = hashlib.md5(
        content.encode("utf-8")
    ).hexdigest()

    old_hash = last_status.get(doctor_id)

    last_status[doctor_id] = status_hash

    if old_hash and old_hash != status_hash:

        message = (
            "🔔 نوبت جدید ممکن است باز شده باشد\n\n"
            f"👨‍⚕️ پزشک: {doctor_name}\n"
            f"🔗 لینک:\n{url}"
        )

        send_telegram(message)

        print(message)

    else:
        print(
            f"{doctor_name}: بدون تغییر"
        )


async def main():

    async with async_playwright() as p:

        browser = await p.chromium.launch(
            headless=True
        )

        page = await browser.new_page()

        while True:

            for doctor in DOCTORS:
                try:
                    await check_doctor(
                        page,
                        doctor
                    )

                except Exception as e:
                    print(
                        "Error:",
                        doctor["name"],
                        e
                    )

            await asyncio.sleep(
                CHECK_INTERVAL
            )


if __name__ == "__main__":
    asyncio.run(main())
