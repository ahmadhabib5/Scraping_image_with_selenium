import argparse
from selenium import webdriver
import os
import time
from PIL import Image
import io
import requests


def scroll_to_end(driver):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)


def image_url_function(string, max_links, driver):
    search_url = "https://www.google.com/search?safe=off&site=&tbm=isch&source=hp&q={q}&oq={q}&gs_l=img"
    driver.get(search_url.format(q=string))
    image_urls = set()
    image_count = 0
    results_start = 0

    while image_count < max_links:
        scroll_to_end(driver)
        thumbnail_results = driver.find_elements_by_css_selector("img.Q4LuWd")
        number_results = len(thumbnail_results)
        print(f"Found: {number_results} search results. Extracting links from {results_start}:{number_results}")

        for img in thumbnail_results[results_start:number_results]:
            try:
                img.click()
                time.sleep(1)
            except Exception:
                continue

            actual_images = driver.find_elements_by_css_selector("img.n3VNCb")
            for actual_image in actual_images:
                if actual_image.get_attribute("src") and "http" in actual_image.get_attribute("src"):
                    image_urls.add(actual_image.get_attribute("src"))

            image_count = len(image_urls)
            if image_count >= max_links:
                print(f"Found: {image_count} image links")
                break
        else:
            print("Found:", image_count, "looking for more image links ...")
            time.sleep(30)
            return

            load_more_button = driver.find_element_by_css_selector(".mye4qd")

            if load_more_button:
                driver.execute_script("document.querySelector('.mye4qd').click();")

        results_start = len(thumbnail_results)

    return image_urls


def save_images(folder_path, file_name, url):
    try:
        image_content = requests.get(url).content

    except Exception as e:
        print(f"ERROR - COULD NOT DOWNLOAD {url} - {e}")

    try:
        image_file = io.BytesIO(image_content)
        image = Image.open(image_file).convert('RGB')

        file_path = os.path.join(folder_path, file_name)

        with open(file_path, 'wb') as f:
            image.save(f, "JPEG", quality=85)
        print(f"SAVED - {url} - AT: {file_path}")
    except Exception as e:
        print(f"ERROR - COULD NOT SAVE {url} - {e}")


def main():
    parser = argparse.ArgumentParser(description="Scraping Image From Google")
    parser.add_argument("--browser_name", help="name of browser", default="mozilla")
    parser.add_argument("--driver_path", help=r"driver location",
                        default=r"webdriver\geckodriver-v0.30.0-win64\geckodriver.exe")
    parser.add_argument("--list_image", help=r"image keyword, ex : cat,dog (separate with comma without num space")
    parser.add_argument("--result_path", help=r"Resul path location", default=r"./image")
    parser.add_argument("--num_images", help="number of images to be scraped", default=20)
    args = parser.parse_args()

    driver_path = args.driver_path

    driver = webdriver.Firefox(executable_path=driver_path)
    search_names = args.list_image.split(",")
    images_path = args.result_path
    number_images = args.num_images
    print("Browser used     :", args.browser_name)
    print("Driver Path      :", driver_path)
    print("list keyword     :", search_names)
    print("result path      :", images_path)
    print("number of images :", number_images)

    for name in search_names:
        if not os.path.isdir(images_path):
            os.mkdir(images_path)
        path = os.path.join(images_path, name)
        if not os.path.isdir(path):
            os.mkdir(path)
        driver.get('https://google.com')
        search_box = driver.find_element_by_css_selector('input.gLFyf')
        search_box.send_keys(name)
        links = image_url_function(name, number_images, driver)
        for i, link in enumerate(links):
            file_name = f"{i:06}.jpg"
            save_images(path, file_name, link)
    driver.quit()


if __name__ == "__main__":
    main()
