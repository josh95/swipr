from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import requests
import json
import os
#I am just a regular human looking for a regular human companion. I am definitely
#not a robot.


def get_credentials():
    credentials = open("credentials.txt", "r").read()
    creds = json.loads(credentials)
    return creds

def download_image(url, personName, index):
    #given a url to an image and the person's id, download it to our pictures directory.
    r = requests.get(url, allow_redirects=True)
    try:
        os.mkdir('pictures/' + personName)
    except:
        print("directory " + personName +" already exists")
    
    open('pictures/' + personName + "/" + str(index) + ".jpeg", 'wb').write(r.content)

def checkNewPerson(matchid):
    #checks if a person's matchId is already in our DB. Returns true if a new person
    return True

def get_imgurls(browser, profileURL, matchid):
    #navigate to profile page and collect img urls for each of that person's photos
    browser.get(profileURL)
    browser.implicitly_wait(2)
    browser.find_element_by_class_name("userinfo2015-thumb").click()

    photos = browser.find_element_by_id("photo_overlay_photos").find_elements_by_tag_name("img")
    for index, photo in enumerate (photos):
        image = photo.get_attribute("src")
        print(image)
        if image is not None:
            download_image(image,matchid, index)

        

def run_bot():

    ##opens up a browser window, signs into OKC, and navigates to the match page.
    browser = webdriver.Firefox()

    browser.get('https://www.okcupid.com/')

    credentials = get_credentials()

    signin = browser.find_element_by_class_name("splashdtf-header-signin-splashButton") # find login button
    signin.click()

    user = browser.find_element_by_id("login_username")
    password = browser.find_element_by_id("login_password")

    user.send_keys(credentials["user"])
    password.send_keys(credentials["pass"])

    browser.find_element_by_id("sign_in_button").click()
    time.sleep(5)

    running = True
    
    while running:
        browser.get('https://www.okcupid.com/match')
        ##find at list of the match cards (links to profiles). Cycle through them until we find one not
        ##already in the database
        browser.implicitly_wait(2)
        people = browser.find_elements_by_class_name("match_card")

        try:
            for person in people:
                matchid = person.get_attribute("id")

                if checkNewPerson(matchid):
                    image = person.find_element_by_tag_name("img").get_attribute("src")
                    profile_url = person.find_element_by_class_name("image_link").get_attribute("href")
                    get_imgurls(browser, profile_url, matchid)
                    break
        except Exception as e:
            print(e)

    
    #browser.quit()


if __name__ == "__main__":
    get_credentials()
    run_bot()
    
