#! /usr/bin/python

import requests
from pyquery import PyQuery as pq
from PIL import Image, ImageDraw, ImageFont
from StringIO import StringIO
import commands
import sys
import os

# url of National Geographic - Photo of the Day site
BASE_URL = "http://photography.nationalgeographic.com/photography/photo-of-the-day"
# url where the downloaded image will be stored
IMAGE_FILE_URL = "/tmp/ngwp.jpg"
# url of a backup image which will be set in case of no Internet connection or other troubles
BACKUP_IMAGE_FILE_URL = "/usr/share/backgrounds/linuxmint-qiana/sayantan_7864647044.jpg"
# url of font used to write the caption of the image
FONT_URL = "/home/andrea/.fonts/Lato-Bold.ttf"
# FONT_URL = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

# download the image from the site
def get_national_geographic():

    try:
        # request the site
        res = requests.get(BASE_URL)
        # print("Request to: %s completed." % res.url)
        # check if the response is good
        if (res.status_code != requests.codes.ok):
            return -1

        # get the url of the image
        site_html = res.text

        site_dom = pq(site_html)
        image_html = site_dom('.primary_photo').find('img')
        image_url = image_html.attr('src').replace("//", "http://")
        image_caption = image_html.attr('alt')

        # get the image
        res = requests.get(image_url)
        # check if the response is good
        if (res.status_code != requests.codes.ok):
            return -1

        image_raw = res.content

        # edit the image (add caption)
        i = Image.open(StringIO(image_raw))
        font = ImageFont.truetype(FONT_URL, 14)
        draw = ImageDraw.Draw(i);
        width = i.size[0] - (6.4 * len(image_caption)) - 10
        height = i.size[1] - 29 - 82
        if ((width >= 0) and (height >= 0)):
            draw.text((width,height), image_caption, (255, 255, 255), font=font)

        # save the image
        i.save(IMAGE_FILE_URL)

        return 0

    except (requests.exceptions.RequestException, requests.exceptions.ConnectionError, requests.exceptions.HTTPError, requests.exceptions.TooManyRedirects, requests.exceptions.Timeout):
        print("Internet error.")
        return -1
    except IOError:
        print("IO error.")
        return -1

def set_wallpaper(url):

    SCHEMA = ""
    # get the desktop environment type
    desktop_env = get_desktop_environment()
    cmd = ""

    if (desktop_env in ["gnome", "unity","cinnamon", "mate"]):
        # set the schema-key depending on the environment
        if desktop_env in ["gnome", "unity"]:
            SCHEMA = "org.gnome.desktop.background picture-uri"
        elif desktop_env=="cinnamon":
            SCHEMA = "org.cinnamon.desktop.background picture-uri"
        elif desktop_env=="mate":
            SCHEMA = "org.mate.background picture-filename"
        #set wallpaper command
        cmd = "gsettings set %s 'file://%s'" % (SCHEMA, url)

    elif (desktop_env in ["fluxbox","jwm","openbox","afterstep"]):
        cmd = "fbsetbg -f %s" % url


    cmd_status, cmd_output = commands.getstatusoutput(cmd)

    if (cmd_status != 0):
        print(cmd_status)
        return -1

    return 0

# useful function to get the principal desktops environment
# thanks to http://stackoverflow.com/a/21213358
def get_desktop_environment():
    if sys.platform in ["win32", "cygwin"]:
        return "windows"
    elif sys.platform == "darwin":
        return "mac"
    else:
        desktop_session = os.environ.get("DESKTOP_SESSION")
        if desktop_session is not None:
            desktop_session = desktop_session.lower()
            if desktop_session in ["gnome","unity", "cinnamon", "mate", "xfce4", "lxde", "fluxbox", "blackbox", "openbox", "icewm", "jwm", "afterstep","trinity", "kde"]:
                return desktop_session
            elif desktop_session.startswith("ubuntu"):
                return "unity"
    return "unknown"


# START
print("Setting the National Geographic, Photo of the Day wallpaper...")

result = get_national_geographic()
if (result == 0): # ng image retrieved
    result = set_wallpaper(IMAGE_FILE_URL)
    if (result != 0): # fail to set the ng image
        result = set_wallpaper(BACKUP_IMAGE_FILE_URL)
else: # set the backup image
    set_wallpaper(BACKUP_IMAGE_FILE_URL)
