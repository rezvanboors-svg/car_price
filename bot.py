import time
import json
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from webdriver_manager.chrome import ChromeDriverManager

# ================= تنظیمات (اینجا را دقیق پر کنید) =================
USERNAME = "نام_کاربری_شما"
PASSWORD = "رمز_عبور_شما"

LOGIN_URL = "https://bourse-trader.ir/login"
PRICE_URL = "https://bourse-trader.ir/car-price"

# مسیر حافظه مرورگر (برای اینکه هر روز لاگین نخواهد)
PROFILE_PATH = os.path.join(os.getcwd(), "chrome_profile")
# ===================================================================

def run_bot():
    print("--- شروع ربات پیشرفته (نسخه نهایی با جزئیات کامل) ---")
    
    options = webdriver.ChromeOptions()
    options.add_argument(f"user-data-dir={PROFILE_PATH}")
    options.add_argument("--start-maximized") 

    # نصب و راه اندازی درایور کروم
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        # 1. ورود به سایت
        driver.get(LOGIN_URL)
        time.sleep(3)

        # بررسی وضعیت لاگین
        if "login" in driver.current_url.lower():
            print("\n" + "="*50)
            print("🛑 نیاز به ورود اولیه!")
            print("1. نام کاربری و رمز را وارد کنید.")
            print("2. کد کپچا را بزنید و وارد شوید.")
            print("3. وقتی وارد پنل شدید، اینجا دکمه ENTER را بزنید.")
            print("="*50 + "\n")
            input("منتظر اینتر شما هستم...")
        else:
            print("✅ ورود خودکار انجام شد.")

        # 2. رفتن به صفحه قیمت‌ها
        print("⏳ در حال بارگذاری لیست خودروها...")
        driver.get(PRICE_URL)
        time.sleep(5) 

        # 3. تغییر تعداد نمایش به ۱۰۰ (برای سرعت بالاتر)
        try:
            dropdown_element = driver.find_element(By.XPATH, "//select[contains(@name, 'length')]")
            select = Select(dropdown_element)
            select.select_by_value('100') 
            print("✅ تنظیم نمایش روی ۱۰۰ عدد.")
            time.sleep(4) # صبر برای اعمال تغییر
        except:
            print("⚠️ منوی تعداد پیدا نشد (با همان ۱۰ تایی ادامه می‌دهیم).")

        # 4. شروع حلقه استخراج (ورق زدن صفحات)
        all_cars_data = []
        page_number = 1
        
        while True:
            print(f"📄 در حال پردازش صفحه {page_number}...")
            
            # پیدا کردن ردیف‌های جدول
            rows = driver.find_elements(By.CSS_SELECTOR, "table tbody tr")
            
            current_page_count = 0
            for row in rows:
                cols = row.find_elements(By.TAG_NAME, "td")
                
                # بررسی تعداد ستون‌ها (مطابق عکس شما)
                # 0:# | 1:برند | 2:مدل | 3:تریم | 4:سال | 5:قیمت
                if len(cols) >= 6:
                    brand = cols[1].text.strip()   # برند (مثل بنز)
                    model = cols[2].text.strip()   # مدل (مثل C200)
                    trim = cols[3].text.strip()    # تریم (مثل توربو)
                    year = cols[4].text.strip()    # سال (مثل 2024)
                    price = cols[5].text.strip()   # قیمت

                    # فیلتر: فقط اگر قیمت معتبر بود ذخیره کن
                    if price and any(char.isdigit() for char in price):
                        all_cars_data.append({
                            "brand": brand,
                            "model": model,
                            "trim": trim,
                            "year": year,
                            "price": price
                        })
                        current_page_count += 1
            
            print(f"   ✅ {current_page_count} خودرو استخراج شد.")

            # === تلاش برای رفتن به صفحه بعد ===
            try:
                # پیدا کردن دکمه Next که غیرفعال (disabled) نباشد
                next_btn = driver.find_element(By.XPATH, "//li[contains(@class, 'next') and not(contains(@class, 'disabled'))]/a")
                
                # کلیک روی دکمه بعدی
                driver.execute_script("arguments[0].click();", next_btn)
                
                print("➡️ رفتن به صفحه بعد...")
                time.sleep(4) # صبر برای لود شدن صفحه جدید
                page_number += 1
                
            except:
                # اگر دکمه بعدی نبود، یعنی کار تمام است
                print(f"🏁 پایان صفحات. (کل صفحات: {page_number})")
                break

        # 5. ذخیره نهایی در فایل
        print(f"\n📊 نتیجه نهایی: {len(all_cars_data)} خودرو پیدا شد.")
        
        if len(all_cars_data) > 0:
            with open("cars.json", "w", encoding="utf-8") as f:
                json.dump(all_cars_data, f, ensure_ascii=False)
            print("✅ فایل cars.json با ساختار جدید و کامل ساخته شد.")
        else:
            print("❌ هیچ خودرویی ذخیره نشد! لطفا ستون‌ها را چک کنید.")

    except Exception as e:
        print(f"\n❌ خطا رخ داد: {e}")

    finally:
        print("بستن برنامه...")
        driver.quit()
        input("برای خروج اینتر بزنید...")

if __name__ == "__main__":
    run_bot()
