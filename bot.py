import time
import json
import os
import traceback
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# ================= تنظیمات =================
LOGIN_URL = "https://bourse-trader.ir/login"
PRICE_URL = "https://bourse-trader.ir/car-price"
PROFILE_PATH = os.path.join(os.getcwd(), "chrome_profile")
# ===========================================

def run_bot():
    print("--- 🚀 شروع ربات (نسخه ضد ضربه و نهایی) ---")
    
    options = webdriver.ChromeOptions()
    options.add_argument(f"user-data-dir={PROFILE_PATH}") 
    options.add_argument("--start-maximized") 
    options.add_argument('--ignore-certificate-errors')

    # راه اندازی درایور
    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        # تایم‌اوت هوشمند ۲۰ ثانیه‌ای برای اینترنت‌های کند
        wait = WebDriverWait(driver, 20) 
    except Exception as e:
        print(f"❌ خطا در باز کردن مرورگر: {e}")
        return

    try:
        # 1. ورود
        print("1️⃣ باز کردن سایت...")
        driver.get(LOGIN_URL)
        time.sleep(3)
        
        if "login" in driver.current_url.lower():
            print("\n🛑 لطفا وارد شوید و اینتر بزنید...")
            input("منتظر اینتر شما هستم...")
        
        # 2. رفتن به قیمت‌ها
        print("2️⃣ رفتن به لیست قیمت‌ها...")
        driver.get(PRICE_URL)
        time.sleep(5) 

        # 3. تلاش برای تغییر به ۱۰۰ تایی (کاملاً ایمن - بدون خروج)
        print("3️⃣ بررسی تنظیمات تعداد نمایش...")
        try:
            # فقط ۵ ثانیه وقت میگذاریم. اگر پیدا نشد، ولش میکنیم
            short_wait = WebDriverWait(driver, 5)
            dropdown = short_wait.until(EC.presence_of_element_located((By.NAME, "DataTables_Table_0_length")))
            Select(dropdown).select_by_value('100') 
            print("✅ موفق: لیست ۱۰۰ تایی شد.")
            # صبر میکنیم تا جدول رفرش شود (چک کردن لود شدن بادی جدول)
            short_wait.until(EC.staleness_of(driver.find_element(By.CSS_SELECTOR, "table tbody tr")))
        except:
            print("⚠️ ناموفق در ۱۰۰ تایی کردن (مهم نیست، با پیش‌فرض سایت ادامه می‌دهیم).")

        all_cars_data = []
        page_number = 1
        last_status_text = "" # آخرین متن Showing ...
        
        while True:
            print(f"\n📄 در حال پردازش صفحه {page_number}...")
            
            # اسکرول به پایین (برای اطمینان از دیده شدن المان‌ها)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)

            # === مرحله حیاتی: چک کردن متن پایین صفحه (Showing X to Y ...) ===
            current_status_text = "Unknown"
            try:
                # تلاش برای پیدا کردن متن وضعیت
                status_elem = driver.find_element(By.CLASS_NAME, "dataTables_info")
                current_status_text = status_elem.text.strip()
                print(f"   ℹ️ وضعیت فعلی: {current_status_text}")
                
                # شرط خروج اصلی:
                # اگر متن صفحه جاری دقیقاً مثل متن صفحه قبلی بود، یعنی درجا زدیم -> خروج
                if current_status_text == last_status_text and page_number > 1:
                    print("🛑 متن پایین صفحه تغییر نکرد (پایان لیست). خروج از حلقه.")
                    break
                
                last_status_text = current_status_text
            except:
                print("⚠️ متن وضعیت پیدا نشد (ریسک ادامه دادن).")

            # === استخراج داده‌ها ===
            try:
                # منتظر میمانیم تا ردیف‌ها قابل رویت باشند
                rows = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "table tbody tr")))
                
                count_in_page = 0
                for row in rows:
                    try:
                        cols = row.find_elements(By.TAG_NAME, "td")
                        if len(cols) >= 6:
                            brand = cols[1].text.strip()
                            model = cols[2].text.strip()
                            trim = cols[3].text.strip()
                            year = cols[4].text.strip()
                            price = cols[5].text.strip()
                            desc = "-"
                            if len(cols) >= 9:
                                desc = cols[8].text.strip() or "-"

                            if price and any(char.isdigit() for char in price):
                                all_cars_data.append({
                                    "brand": brand, "model": model, "trim": trim,
                                    "year": year, "price": price, "desc": desc
                                })
                                count_in_page += 1
                    except:
                        continue # اگر یک ردیف خراب بود، بعدی را بگیر
                print(f"   ✅ {count_in_page} خودرو استخراج شد.")
            except Exception as e:
                print(f"❌ خطا در خواندن جدول: {e}")

            # === رفتن به صفحه بعد ===
            try:
                # پیدا کردن دکمه Next (با ۳ روش مختلف)
                next_btn = None
                selectors = [
                    (By.CSS_SELECTOR, ".dataTables_paginate .next"), # روش ۱
                    (By.ID, "DataTables_Table_0_next"),             # روش ۲
                    (By.XPATH, "//a[contains(text(),'Next')]"),      # روش ۳
                    (By.XPATH, "//a[contains(text(),'بعدی')]")       # روش ۴
                ]

                for method, selector in selectors:
                    try:
                        btn = driver.find_element(method, selector)
                        if btn.is_displayed():
                            next_btn = btn
                            break
                    except:
                        continue

                # اگر دکمه کلا نبود -> پایان
                if not next_btn:
                    print("🏁 دکمه بعدی پیدا نشد (پایان).")
                    break

                # چک کردن کلاس disabled (غیرفعال بودن)
                if "disabled" in next_btn.get_attribute("class"):
                    print("🏁 دکمه Next غیرفعال شد (پایان).")
                    break

                # کلیک روی لینک داخل دکمه
                try:
                    link = next_btn.find_element(By.TAG_NAME, "a")
                except:
                    link = next_btn # اگر لینک نداشت خود دکمه رو بزن

                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", link)
                time.sleep(0.5)
                driver.execute_script("arguments[0].click();", link)
                print("➡️ کلیک شد...")

                # === انتظار هوشمند برای تغییر صفحه ===
                # اینجا به ربات میگوییم: صبر کن تا متن "Showing..." تغییر کند
                try:
                    wait.until(lambda d: d.find_element(By.CLASS_NAME, "dataTables_info").text.strip() != current_status_text)
                    print("✅ صفحه با موفقیت تغییر کرد.")
                    page_number += 1
                    # یک مکث کوتاه برای اطمینان از رندر شدن کامل جدول
                    time.sleep(1) 
                except:
                    print("⚠️ زمان انتظار تمام شد و متن تغییر نکرد (احتمالا پایان لیست).")
                    break
                    
            except Exception as e:
                print(f"🏁 خروج اضطراری: {e}")
                break

        # ذخیره نهایی
        print(f"\n📊 نتیجه نهایی: {len(all_cars_data)} خودرو.")
        if len(all_cars_data) > 0:
            with open("cars.json", "w", encoding="utf-8") as f:
                json.dump(all_cars_data, f, ensure_ascii=False)
            print("✅ فایل cars.json با موفقیت ساخته شد.")
        else:
            print("❌ لیست خالی است.")

    except Exception as e:
        print(f"\n❌ خطای غیرمنتظره: {e}")
        traceback.print_exc()
    finally:
        if 'driver' in locals():
            try: driver.quit()
            except: pass
        input("اینتر بزنید...")

if __name__ == "__main__":
    run_bot()
