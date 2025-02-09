from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service 
from selenium.webdriver.common.by import By 
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC 
import time
import re
import random
import os
import json

def zapis_zaznamy(soubor, produkt, záznam):
    try:
        with open(soubor, "a", encoding="utf-8") as f:
            f.write(f"    Název: {produkt}\n")
            f.write(f"      Záznam:\n")
            f.write(f"        Čas: {záznam['Čas']}\n")
            f.write(f"        Cena (Kč): {záznam['Cena (Kč)']}\n")
            f.write(f"        Hodnocení: {záznam['Hodnocení']}\n")
            f.write(f"        Dostupnost: {záznam['Dostupnost']}\n")
            f.write(f"        URL: {záznam['URL']}\n")
            f.write("\n")
        print(f"Záznam pro '{produkt}' úspěšně zapsán do '{soubor}'.")
    except Exception as e:
        print(f"Chyba při zapisování do souboru: {e}")

service = Service(executable_path="chromedriver.exe")
driver = webdriver.Chrome(service=service)

# kategorie_urls = {
#     "Mobilní telefony": {
#         "Apple iPhone 13": "https://www.alza.cz/mobilni-telefony-apple-iphone-13/18892046.htm?evt=re&exps=iphone+13",
#         "Google Pixel": "https://www.alza.cz/mobilni-telefony-google-pixel/18910327.htm",
#     },
#     "Herní konzole": {
#         "Playstation 5": "https://www.alza.cz/gaming/herni-konzole-playstation-5/18876712.htm"
#     }
# }

with open("kategorie_urls.json", "r", encoding="utf-8") as f:
    kategorie_urls = json.load(f)


soubor_cesta = "produkty_hierarchie.txt"
if not os.path.exists(soubor_cesta):
    open(soubor_cesta, "w", encoding="utf-8").close()

try:

    driver.get(list(kategorie_urls["Mobilní telefony"].values())[0])
    prijmout_cookies = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, ".cookies-info__button.js-cookies-info-accept"))
    )
    prijmout_cookies.click()
    print("Kliknutí na cookies")

    for hlavni_kategorie, podkategorie in kategorie_urls.items():
        for podkategorie_nazev, podkategorie_url in podkategorie.items():
            driver.get(podkategorie_url)
            print(f"Zpracovávám kategorii: {hlavni_kategorie} -> {podkategorie_nazev}")

            produkt_elementy = driver.find_elements(By.CLASS_NAME, "box.browsingitem.js-box.canBuy.inStockAvailability")
            produkt_urls = [
                produkt.find_element(By.TAG_NAME, "a").get_attribute("href")
                for produkt in produkt_elementy
            ]

            for produkt_url in produkt_urls:
                driver.get(produkt_url)

                nazev_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "h1.h1-placeholder"))
                )
                nazev = nazev_element.text

                cena_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "price-box__price"))
                )
                cena_text = cena_element.text
                cena = re.sub(r'[^0-9]', '', cena_text)
                cena = int(cena)

                try:
                    hodnoceni_element = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "star-rating-wrapper"))
                    )
                    hodnoceni = hodnoceni_element.get_attribute("data-rating")
                    hodnoceni = hodnoceni.replace(",", ".")
                    hodnoceni = round(float(hodnoceni) * 5, 1)
                except Exception:
                    hodnoceni = "Neznámé"

                try:
                    dostupnost_element = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "availability-alz-30"))
                    )
                    dostupnost_text_element = dostupnost_element.find_element(By.CLASS_NAME, "AlzaText")
                    dostupnost = dostupnost_text_element.text.strip()
                except Exception:
                    dostupnost = "Neznámé"

                záznam = {
                    "Čas": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "Cena (Kč)": cena,
                    "Hodnocení": hodnoceni,
                    "Dostupnost": dostupnost,
                    "URL": produkt_url
                }

                zapis_zaznamy(soubor_cesta, nazev, záznam)

                zpozdeni = random.uniform(5, 15)
                time.sleep(zpozdeni)

except Exception as e:
    print(f"Chyba: {e}")

finally:
    driver.quit()
