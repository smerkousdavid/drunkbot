import urllib3
from bs4 import BeautifulSoup as bs
from urllib.parse import quote
import random


def get_image(urll):
    http = urllib3.PoolManager()
    urls = http.request('GET', urll)  # , headers=headers)
    print("Data length %d" % len(urls.data))
    soup = bs(str(urls.data), "lxml")
    images = soup.findAll("img")
    return str(random.choice(images)["src"])


# noinspection PyBroadException
def execute(args: list):
    global words
    types = "image"
    try:
        types = str(args[0])
    except Exception:
        print("I guess i'm selecting an image...")

    try:
        if types == "image":
                words = open("command_package/words.txt", "r").read().splitlines()
                word = str(random.choice(words))
                print("Selected word %s" % word)

                encoded_url = "http://www.picsearch.com/index.cgi?q={0}".format(
                    str(quote(word)))
                print("Request url: %s" % encoded_url)
        else:
            encoded_url = ""

        '''
        print(data)
        pattern = re.compile('imgurl=([^>]+)&amp;imgrefurl')
        image_list = pattern.findall(data)
        print("Found %d images" % len(image_list))
        index = random.randint(0, len(image_list)-1)
        final_url = image_list[index]
        print("Final image url is: %s" % final_url)

        data = json.load(urls)
        print("Got from google %s " % data)
        urls.close()

        results = data['responseData']['results']
        url = results[random.randint(0, len(results) - 1)]['url']
        urlretrieve(url, './image')

        imagetype = imghdr.what('./image')
        if not (type(imagetype) is None):
            os.rename('./image', './image.' + imagetype)
        '''

        return get_image(encoded_url)
    except Exception:
        try:
            word = str(random.choice(words))
            print("Selected word %s" % word)

            encoded_url = "http://www.picsearch.com/index.cgi?q={0}".format(
                str(quote(word)))
            print("Request url: %s" % encoded_url)
            return get_image(encoded_url)
        except Exception:
            return "What did you say***!!!*** I couldn't understand you..."
