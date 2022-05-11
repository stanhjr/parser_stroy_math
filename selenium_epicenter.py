import pickle
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait


async def set_cookies_for_epicenter():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--headless")
    prefs = {"profile.default_content_setting_values.notifications": 2}
    chrome_options.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=chrome_options)

    driver.maximize_window()
    driver.get("https://epicentrk.ua/shop/ekstruzionnyy-penopolistirol-ekoplit-standart-1180x580x50mm.html")
    wait = WebDriverWait(driver, 10)
    wait.until(ec.presence_of_element_located((By.CLASS_NAME, "header__locations-opener"))).click()

    wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, "body > div.popup._I8vU4b > div > div > div._AqFRW2 > div._nowYXF > div > div._k4oONZ"))).click()
    wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, "body > div.popup._I8vU4b > div > div > div._AqFRW2 > div._nowYXF > div > div._mxtoHY > div > input"))).send_keys('Днепр')
    wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, "body > div.popup._I8vU4b > div > div > div._AqFRW2 > div._nowYXF > div > div._mxtoHY > div._Aqju_l > div > div:nth-child(1)"))).click()
    driver.execute_script("window.scrollTo(0, -500)")
    time.sleep(3)
    wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, "body > div.popup._I8vU4b > div > div > div._AqFRW2 > div._Yx7OxZ > div > div > div > div:nth-child(3) > button"))).click()

    # time.sleep(12)
    pickle.dump(driver.get_cookies(), open("cookies.pkl", "wb"))
    driver.close()
    return True
