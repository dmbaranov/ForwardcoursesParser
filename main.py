import os
import sys
import time
import requests
from getpass import getpass
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains


def login(drv):
    login = input("Enter login: ")
    password = getpass("Enter password: ")
    input_login = drv.find_element_by_name("user[email]")
    input_password = drv.find_element_by_name("user[password]")
    button_submit = drv.find_element_by_name("commit")

    input_login.send_keys(login)
    input_password.send_keys(password)
    button_submit.click()


def download_file(url, title, index):
    print("Downloading")
    file_name = title + "/" + "Chapter " + str(index) + ".mp4"

    with open(file_name, "wb") as f:
        start = time.clock()
        r = requests.get(url, stream=True)
        total_length = r.headers.get("content-length")
        dl_time = 0

        if total_length is None:
            f.write(r.content)
        else:
            downloaded = 0
            total_length = int(total_length) // 1024 // 1024

            for data in r.iter_content(chunk_size=4096):
                dl_time += len(data)
                downloaded += len(data) / 1024 / 1024
                downloaded_percentage = downloaded * 100 // total_length
                f.write(data)
                sys.stdout.write("\r[{0}{1}] {2}%, {3:.2f}mbps".format("*" * int(downloaded_percentage // 10),
                                                                   "-" * int(10 - downloaded_percentage // 10),
                                                                   int(downloaded_percentage),
                                                                   dl_time // (time.clock() - start) / 1024 / 1024 / 10))
                sys.stdout.flush()


def get_video_url(drv):
    chapters = drv.find_elements_by_class_name("time-codes-item")
    result = []

    for chapter in chapters:
        link = chapter.find_element_by_tag_name("a")
        link.click()
        time.sleep(5)
        video_wrapper = drv.find_element_by_class_name("wistia_click_to_play")
        video = video_wrapper.find_element_by_tag_name("source")
        print(link.text + ": " + video.get_attribute("src"))
        result.append(video.get_attribute("src"))

    return result

driver = webdriver.Firefox()
action_chains = ActionChains(driver)

driver.get("https://forwardcourses.com/users/sign_in")
time.sleep(4)

login(driver)
time.sleep(4)

links = []
with open("links.txt") as file:
    links.append(file.readline())

for link in links:
    driver.get(link)
    time.sleep(5)
    title = driver.find_element_by_class_name("single-title").text
    if os.path.exists(title):
        continue
    os.makedirs(title)

    chapters = get_video_url(driver)
    i = 1
    for chapter_url in chapters:
        print("\nProcessing {0}, chapter{1}".format(title, i))
        download_file(chapter_url, title, i)
        i += 1

    print("\n")

