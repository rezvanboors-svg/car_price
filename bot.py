import time
import json
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains

# ================= تنظیمات =================
# آدرس صفحه ورود
LOGIN_URL = "https://bourse-trader.ir/login"
# آدرس صفحه قیمت (طبق تصویر شما)
PRICE_URL = "https://bourse-trader.ir/car-price"

# مسیر ذخیره حافظه مرورگر (برای اینکه لاگین نپرد)
PROFILE_PATH = os.path.join(os.getcwd(), "chrome_profile")
# ===========================================

def run_bot():
    print("--- 🚀 شروع ربات استخراج خودرو ---")
    
    # تنظیمات مرورگر
    options = webdriver.ChromeOptions()
    options.add_argument(f"user-data-dir={PROFILE_PATH}") 
    options.add_argument("--start-maximized") 

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        # 1. مدیریت ورود (Login) و کپچا
        driver.get(LOGIN_URL)
        time.sleep(3)
        
        # اگر ربات دید که در صفحه لاگین هستید، صبر می‌کند
        if "login" in driver.current_url.lower():
            print("\n" + "="*60)
            print("🛑 حالت تعاملی فعال شد (حل کپچا)")
            print("1. لطفا نام کاربری و رمز عبور خود را وارد کنید.")
            print("2. کد کپچا را حل کنید و دکمه ورود را بزنید.")
            print("3. >> وقتی کاملاً وارد سایت شدید، اینجا دکمه ENTER را بزنید <<")
            print("="*60 + "\n")
            input("منتظر اینتر شما هستم...")
        else:
            print("✅ تشخیص ورود خودکار (از قبل لاگین بودید).")

        # 2. رفتن به صفحه قیمت‌ها
        print("⏳ در حال بارگذاری صفحه قیمت‌ها...")
        driver.get(PRICE_URL)
        time.sleep(5) 

        # 3. تغییر تعداد نمایش به ۱۰۰ (طبق اسکرین‌شات شما)
        try:
            # پیدا کردن منوی کشویی Show entries
            dropdown = driver.find_element(By.XPATH, "//select[contains(@name, 'length')]")
            Select(dropdown).select_by_value('100') 
            print("✅ لیست روی حالت ۱۰۰ تایی تنظیم شد.")
            time.sleep(5) # صبر بیشتر برای لود شدن لیست طولانی
        except Exception as e:
            print(f"⚠️ نتوانستیم لیست را ۱۰۰ تایی کنیم (با ۱۰ تایی ادامه می‌دهیم). خطا: {e}")

        all_cars_data = []
        page_number = 1
        
        # 4. حلقه استخراج (ورق زدن اتوماتیک)
        while True:
            print(f"📄 در حال اسکن صفحه {page_number}...")
            
            # اسکرول به پایین صفحه (برای اینکه دکمه Next لود شود)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)

            # پیدا کردن جدول و ردیف‌ها
            rows = driver.find_elements(By.CSS_SELECTOR, "table tbody tr")
            
            for row in rows:
                cols = row.find_elements(By.TAG_NAME, "td")
                
                # طبق تصویر ارسالی شما، جدول ۱۰ ستون دارد. ما ستون‌های اصلی را می‌خواهیم:
                # ستون ۲: نوع (برند) | ستون ۳: مدل | ستون ۴: تریم | ستون ۵: سال | ستون ۶: قیمت
                if len(cols) >= 6:
                    brand = cols[1].text.strip()
                    model = cols[2].text.strip()
                    trim = cols[3].text.strip()
                    year = cols[4].text.strip()
                    price = cols[5].text.strip()

                    # فیلتر: فقط اگر قیمت معتبر بود (عدد داشت) ذخیره کن
                    if price and any(char.isdigit() for char in price):
                        all_cars_data.append({
                            "brand": brand,
                            "model": model,
                            "trim": trim,
                            "year": year,
                            "price": price
                        })

            print(f"   ✅ جمع کل خودروهای پیدا شده تا الان: {len(all_cars_data)}")

            # 5. زدن دکمه صفحه بعد (Next)
            try:
                # پیدا کردن دکمه Next که کلاس disabled نداشته باشد
                next_btn = driver.find_element(By.XPATH, "//li[contains(@class, 'next') and not(contains(@class, 'disabled'))]/a")
                
                # کلیک روی دکمه (استفاده از جاوااسکریپت برای اطمینان بیشتر)
                driver.execute_script("arguments[0].click();", next_btn)
                
                print("➡️ رفتن به صفحه بعد...")
                time.sleep(4) # صبر برای لود صفحه جدید
                page_number += 1
            except:
                print("🏁 دکمه بعدی پیدا نشد یا غیرفعال است (پایان لیست).")
                break

        # 6. ذخیره فایل نهایی
        print(f"\n📊 نتیجه نهایی: {len(all_cars_data)} خودرو استخراج شد.")
        if len(all_cars_data) > 0:
            with open("cars.json", "w", encoding="utf-8") as f:
                json.dump(all_cars_data, f, ensure_ascii=False)
            print("✅ فایل cars.json با موفقیت ساخته شد.")
        else:
            print("❌ هیچ خودرویی ذخیره نشد. لطفا ساختار سایت را بررسی کنید.")

    except Exception as e:
        print(f"❌ خطای ناگهانی: {e}")
    finally:
        driver.quit()
        input("عملیات تمام شد. برای بستن پنجره اینتر بزنید...")

if __name__ == "__main__":
    run_bot()
