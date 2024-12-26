# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.action_chains import ActionChains
# import requests
# import io
# from PIL import Image
# import time
# import pandas as pd
# import urllib.parse
# import concurrent.futures
# import json

# def setup_driver(chromedriver_path):
#     service = Service(chromedriver_path)
#     options = webdriver.ChromeOptions()
#     options.add_argument("--headless")  
#     options.add_argument("--disable-gpu")
#     options.add_argument("--no-sandbox")
#     driver = webdriver.Chrome(service=service, options=options)
#     return driver

# def get_images_from_google(driver, delay, max_images, movie_name):
#     def scroll_down(driver):
#         driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
#         time.sleep(delay)

    
#     encoded_movie_name = urllib.parse.quote(movie_name)
#     url = f"https://www.google.com/search?q={encoded_movie_name}%20netflix&tbm=isch"
#     driver.get(url)
    
#     image_urls = set()
#     skips = 0
    
#     while len(image_urls) + skips < max_images:
#         scroll_down(driver)
        
#         thumbnails = driver.find_elements(By.CLASS_NAME, "H8Rx8c")
        
#         for img in thumbnails[len(image_urls) + skips:max_images]:
#             try:
#                 ActionChains(driver).move_to_element(img).click().perform()
#                 time.sleep(delay)
#             except:
#                 continue

#             divs = driver.find_elements(By.CLASS_NAME, "YsLeY")
            
#             for div in divs:
#                 image = div.find_elements(By.TAG_NAME, 'img')[0]
#                 attr = image.get_attribute('src')
                
#                 if attr in image_urls:
#                     max_images += 1
#                     skips += 1
#                     break

#                 if attr and 'http' in attr:
#                     image_urls.add(attr)
    
#     return list(image_urls)


# def get_links_for_titles(titles):
#     driver = setup_driver('./chromedriver')
#     image_urls = [None] * len(titles)
#     for i, title in enumerate(titles):
#         image_url = get_images_from_google(driver, 1, 3, title)[0]
#         print(image_url)
#         image_urls[i] = image_url

#     driver.quit()  
#     return image_urls

def get_links_with_api(titles):
    image_urls = [None] * len(titles)
    for i, title in enumerate(titles):
        encoded_movie_name = urllib.parse.quote(title)
        api_link = f"http://www.omdbapi.com/?t={encoded_movie_name}&apikey=197659c0"
        response = requests.get(api_link)
        poster = json.loads(response.text)
        if "Poster" in poster:
            image_urls[i] = poster["Poster"]
        else:
            print(title)
            image_urls[i] = None
    return image_urls

# def download_images_for_titles(titles):
#     with concurrent.futures.ThreadPoolExecutor() as executor:
#         futures = []
        
#         for title in titles:
#             futures.append(executor.submit(get_links_for_titles, title))
        
#         concurrent.futures.wait(futures)