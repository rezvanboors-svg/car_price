import time
import json
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

# ================= تنظیمات =================
# اینجا نام کاربری و رمز خود را وارد کنید
USERNAME = "نام_کاربری_شما"
PASSWORD = "رمز_عبور_شما"

# آدرس‌ها
LOGIN_URL = "https://bourse-trader.ir/login"
PRICE_URL = "https://bourse-trader.ir/car-price"

# پوشه‌ای برای ذخیره لاگین (که هر روز نخواهید لاگین کنید)
# این پوشه در کنار فایل برنامه ساخته می‌شود
PROFILE_PATH = os.path.join(os.getcwd(), "chrome_profile")
# ===========================================

def run_bot():
    print("--- شروع ربات ---")
    
    # تنظیمات مرورگر برای ذخیره سشن (حافظه)
    options = webdriver.ChromeOptions()
    options.add_argument(f"user-data-dir={PROFILE_PATH}")
    options.add_argument("--start-maximized") # تمام صفحه شدن

    # دانلود و نصب خودکار درایور کروم
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        # 1. رفتن به سایت
        driver.get(LOGIN_URL)
        time.sleep(3)

        # بررسی می‌کنیم که آیا قبلا لاگین هستیم یا نه؟
        # اگر در آدرس صفحه کلمه login بود، یعنی باید لاگین کنیم
        if "login" in driver.current_url.lower():
            print("\n" + "!"*50)
            print("🛑 نیاز به ورود اولیه!")
            print("لطفا در مرورگر باز شده:")
            print("1. نام کاربری و رمز را وارد کنید.")
            print("2. کد کپچا را وارد کنید.")
            print("3. دکمه ورود را بزنید.")
            print("✅ وقتی کاملا وارد پنل شدید، بیایید اینجا و دکمه Enter کیبورد را بزنید.")
            print("!"*50 + "\n")
            
            # منتظر می‌مانیم تا شما اینتر بزنید
            input("منتظر اینتر شما هستم...")
        else:
            print("✅ از قبل لاگین بودید، ادامه می‌دهیم...")

        # 2. رفتن به صفحه قیمت
        print("⏳ در حال دریافت قیمت‌ها...")
        driver.get(PRICE_URL)
        time.sleep(4) # صبر برای لود کامل

        # 3. استخراج جدول
        cars_data = []
        # تلاش برای پیدا کردن تمام ردیف‌های جدول
        rows = driver.find_elements(By.TAG_NAME, "tr")

        print(f"تعداد ردیف‌های پیدا شده: {len(rows)}")

        for row in rows:
            cols = row.find_elements(By.TAG_NAME, "td")
            # اگر ردیف دارای ستون‌های کافی بود (نام، مدل، قیمت)
            if len(cols) >= 3:
                name = cols[0].text.strip()
                model = cols[1].text.strip()
                price = cols[2].text.strip()

                # اگر قیمت خالی نبود، اضافه کن
                if price and price != "-":
                    cars_data.append({
                        "name": name,
                        "model": model,
                        "price": price
                    })

        # 4. ذخیره فایل
        if len(cars_data) > 0:
            with open("cars.json", "w", encoding="utf-8") as f:
                json.dump(cars_data, f, ensure_ascii=False)
            print(f"\n✅ موفقیت! اطلاعات {len(cars_data)} خودرو در فایل cars.json ذخیره شد.")
        else:
            print("\n❌ جدولی پیدا نشد یا خالی بود.")

    except Exception as e:
        print(f"\n❌ خطا رخ داد: {e}")

    finally:
        # بستن مرورگر
        print("بستن برنامه...")
        driver.quit()
        input("برای خروج اینتر بزنید...")

if __name__ == "__main__":
    run_bot()