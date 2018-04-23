from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import requests
import json
#I am just a regular human looking for a regular human companion. I am definitely
#not a robot.


def get_credentials():
    credentials = open("credentials.txt", "r").read()
    creds = json.loads(credentials)
    return creds

def download_image(url, personName):

    r = requests.get(url, allow_redirects=True)
    open('pictures/'+personName + ".jpeg", 'wb').write(r.content)

def run_bot():


    browser = webdriver.Firefox()

    browser.get('https://www.okcupid.com/')

    #assert 'Yahoo' in browser.title

    credentials = get_credentials()

    signin = browser.find_element_by_class_name("splashdtf-header-signin-splashButton") # find login button
    signin.click()


    user = browser.find_element_by_id("login_username")
    password = browser.find_element_by_id("login_password")

    user.send_keys(credentials["user"])
    password.send_keys(credentials["pass"])

    browser.find_element_by_id("sign_in_button").click()
    time.sleep(5)
    browser.get('https://www.okcupid.com/match')

    browser.implicitly_wait(2)
    people = browser.find_elements_by_class_name("match_card")
    for person in people:
        matchid = person.get_attribute("id")
        image = person.find_element_by_tag_name("img").get_attribute("src")
        download_image(image,matchid)
        
    #browser.quit()


if __name__ == "__main__":
    get_credentials()
    
