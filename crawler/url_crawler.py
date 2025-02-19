from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
import time

from crawler_utils import load_driver


def search_by_keyword(keyword:str):
    url = f"https://search.naver.com/search.naver?ssc=tab.news.all&where=news&query={keyword}"

    return url

def get_news_url(driver, url, query_n:int, wait_time=5, delay_time=0.5) -> list[str]:
    news_urls = []

    driver.get(url)
    driver.implicitly_wait(wait_time)

    while True:
        news_elements = driver.find_elements(By.CSS_SELECTOR, 'a.info:not(.press)')
        news_n = len(news_elements)
        print("요청 n:", query_n, "기사 n: ", news_n)

        if query_n <= news_n:
            for element in news_elements[:query_n]:  # query_n개만큼 가져옴
                news_url = element.get_attribute('href')
                news_urls.append(news_url)
            break

        try:
            parent_li = news_elements[-1].find_element(By.XPATH, "./ancestor::li")
            current_id = int(parent_li.get_attribute('id')[6:])

            target_id = current_id + 3 * (query_n - news_n)  # 예상 ID 계산

            scroll_script = f"""
                // 현재 화면에 보이는 마지막 요소의 위치 가져오기
                let currentElement = document.getElementById('sp_nws{current_id}');
                let currentPos = currentElement.getBoundingClientRect().top;

                // 예상되는 다음 요소들의 간격을 계산하여 스크롤
                let estimatedHeight = currentElement.offsetHeight;
                let numberOfSteps = {target_id - current_id};
                let scrollAmount = currentPos + (estimatedHeight * numberOfSteps * 1.2); // 여유있게 1.2배

                window.scrollBy(0, scrollAmount);
            """

            driver.execute_script(scroll_script)
            time.sleep(delay_time)

        except NoSuchElementException:
            print("스크롤할 요소를 찾을 수 없음.")
            break
        except Exception as e:
            print(f"예상치 못한 오류 발생: {e}")
            raise

    return news_urls



if __name__ == '__main__':
    driver = load_driver()
    keyword, number = input("검색하실 키워드를 입력해주세요: "), int(input("크롤링할 뉴스 기사의 개수를 입력해주세요: "))

    url = search_by_keyword(keyword)
    news_urls_list = get_news_url(driver, url, number)
    print(news_urls_list)