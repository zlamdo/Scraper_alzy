# Scraper Alzy  

Tento projekt se skládá ze dvou hlavních částí:  

## Sběr dat o produktech z Alza.cz pomocí Selenium  

Skript automaticky prochází zadané kategorie produktů na Alza.cz a extrahuje informace o:  
- **Ceně**  
- **Hodnocení**  
- **Dostupnosti**  
- **Dalších parametrech**  

Výsledky se ukládají do souboru `produkty_hierarchie.txt` pro další zpracování.  

### Použité knihovny:  
- `selenium` (automatizace webového prohlížeče)  
- `re`, `json`, `datetime`, `time`, `random`, `os` (práce s daty, soubory a časem)  


## Webová aplikace pro vyhledávání a analýzu cen produktů  

### Funkce:  
**Přihlášení a registrace uživatelů**  
**Vyhledávání produktů podle kritérií (název, cena, hodnocení, datum)**  
**Filtrování výsledků**  
**Možnost přidávat nové URL produktů ke sledování**  
**Funkce Vývoj ceny – graf změn cen v čase**  

### Použité knihovny:  
- `Flask`  
- `matplotlib`, `io`, `base64` 
- `functools`, `os`, `json`  

##To-Do List
🔲 Scrapovat více informací
🔲 upozornění uživatele e-mailem pokud cena klesne pod určitou hranici
🔲 Možnost sledovat více e-shopů
🔲 Automatizovaný scraping pomocí cron
🔲 Šifrování hesel
