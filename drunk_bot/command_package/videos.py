from os.path import dirname
from os import listdir
from os.path import isfile, join

'''
from time import sleep
from bs4 import BeautifulSoup
from splinter import Browser
'''


# noinspection PyBroadException
def execute(args: list):
    video_upload = None
    try:
        video_upload = str(args[0])
    except Exception:
        pass

    try:
        path = dirname(__file__).replace("command_package", "videos")
        print(path)
        dir_list = listdir(path)
        files = [("[%d] : %s" % (i, f.replace('.mp4', '').replace('\n', '')))
                 for i, f in enumerate(dir_list) if isfile(join(path, f))]

        if video_upload:
            pass

        return "**Videos downloaded:** \n**--------------------------------------**\n```%s```" \
               "\n" % str(',\n'.join(files))

    except Exception as err:
        return "Couldn't list the videos... %s" % str(err.args[0])


"""
with Browser('chrome') as browser:
    url = "http://expirebox.com/"
    browser.visit(url)
    path = dirname(__file__) + "/"#.replace("command_package", "videos")
    browser.attach_file('files[]', path + "/words.txt") # + listdir(path)[1])
    while browser.is_element_not_present_by_id("progress"):
        print("waiting for progress")
        sleep(0.2)
    print("found progress bar")
    while True:
        soup = BeautifulSoup(browser.html, "lxml")
        div = soup.find_all("div", {"class": "pct"})[0].text
        percentage = div.split()[0]
        print(percentage)
        if "finish" in percentage:
            break
        sleep(0.4)
    print("Done uploading")
    soup = BeautifulSoup(browser.html, "lxml")
    xpath = "//div[@class=\"input-group-btn\"]"
    while browser.is_element_not_present_by_xpath(xpath):
        print("Waiting for download button")
        sleep(0.2)
    print("Found download button!!!")
    buttons = browser.find_by_tag("button")
    check = ["Download", "link"]
    for button in buttons:
        if all(s in str(button.text) for s in check):
            button.click()
            print("Clicked download button")
            break

    sleep(1)

    while True:
        soup = BeautifulSoup(browser.html, "lxml")
        link = soup.find_all("div", {"class": "download-button-wrapper"})
        print(link)
        sleep(3)

    xpath = "//div[@class=\"download-button-wrapper text-center\"]/a"
    while browser.is_element_not_present_by_xpath(xpath):
        print("Waiting for download button (final)")
        sleep(0.2)
    print(browser.html)
    links = browser.find_by_xpath(xpath)
    print("LINKS %s" % str(links))
    for link in links:
        try:
            print(link['href'])
        except:
            pass
    print("END LINKS")
    download_link = None
    links = browser.find_by_tag("a")
    check = ["btn-primary", "btn"]


    for link in links:
        print(link['class'])
        if all(s in str(link['class']) for s in check):
            download_link = str(link['href'])
            break
    if download_link:
        download_link = url + download_link
        print("Got link! %s" % download_link)
    else:
        print("Couldn't get it!!")
    sleep(10)
    #browser.find_by_id("fileupload").click()

    #browser.quit()"""
