import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

insta_url = "https://www.instagram.com/explore/tags/"
initial_hashtag = "dog"
max_hastags = 20
INSTA_LOGIN_IMFOMATION = [
]
browser = webdriver.Chrome(ChromeDriverManager().install())
counted_hastags = []
used_hastags = []


def wait_for(locator):
    return WebDriverWait(browser, 5).until(
        EC.presence_of_element_located(locator)
    )


def wait_for_all(locator):
    return WebDriverWait(browser, 5).until(
        EC.presence_of_all_elements_located(locator)
    )


def insta_login():
    browser.get("https://www.instagram.com/accounts/login/")
    insta_login_inputs = wait_for_all((By.CLASS_NAME, "_2hvTZ"))
    for idx, login_input in enumerate(insta_login_inputs):
        login_input.send_keys(INSTA_LOGIN_IMFOMATION[idx])
    insta_login_inputs[1].send_keys(Keys.ENTER)


def get_results(target_hashtag, result_count=10):
    insta_search_input = browser.find_element_by_class_name("x3qfX")
    insta_search_input.send_keys(f"#{target_hashtag}")
    try:
        results = wait_for_all((By.CLASS_NAME, "-qQT3"))
        for result in results:
            hashtag = result.text.split()[0][1:]
            post_count = int(result.text.split()[1].replace(",", ""))
            if hashtag != target_hashtag and hashtag not in used_hastags and post_count > 50:
                browser.execute_script(
                    f"window.open('{insta_url + hashtag}')"
                )
                if len(browser.window_handles) == result_count:
                    break
    except:
        insta_search_input.clear()
        get_results(initial_hashtag)


def extract_data():
    try:
        hashtag_name = wait_for((By.TAG_NAME, "h1"))
        post_count = wait_for((By.CLASS_NAME, "g47SY"))
        if post_count:
            post_count = int(post_count.text.replace(",", ""))
        if hashtag_name:
            hashtag_name = hashtag_name.text[1:]
        if hashtag_name and post_count:
            counted_hastags.append((hashtag_name, post_count))
            used_hastags.append(hashtag_name)
    except Exception:
        pass


def get_related(target_url):
    get_results(target_url.rstrip("/").split("/")[-1])
    for window in browser.window_handles[:-1]:
        browser.switch_to.window(window)
        extract_data()
        browser.close()
        time.sleep(2)
        if len(used_hastags) == max_hastags:
            break
    if len(used_hastags) < max_hastags:
        browser.switch_to.window(browser.window_handles[0])
        get_related(browser.current_url)


def start(target_url):
    insta_login()
    time.sleep(3)
    browser.get(target_url)
    get_related(target_url)


start(f"{insta_url + initial_hashtag}")
