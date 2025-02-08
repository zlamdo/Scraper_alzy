from selenium import webdiver
from selenium.webdriver.chrome.service import Service
import time
service=Service(executable_path="chromedriver.exe")
driver=webdiver.Chrome(service=service)

driver.get("https://google.com")
time.sleep(10)
driver.quit()