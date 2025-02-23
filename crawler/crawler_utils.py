from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

options = Options()

# selenium 동한 동적 크롤링 시
def load_driver():
    service = Service()

    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")
    options.add_argument("--start-maximized")
    options.add_experimental_option('detach', True)

    driver = webdriver.Chrome(service=service, options=options)

    return driver


# TODO 6개 대분야에서 상위 n개 뉴스의 url을 크롤링해오는 코드 작성 필요
def get_html(driver, url, wait_time=5):
    driver.implicitly_wait(wait_time)
    driver.get(url)

    html = driver.execute_script("return document.documentElement.outerHTML;")

    return html

# bs4 통한 정적 크롤링 시
def get_soup(url) -> BeautifulSoup:
    import requests

    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(response.text, "html.parser")

    return soup