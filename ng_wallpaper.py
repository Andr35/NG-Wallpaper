#! /usr/bin/python

import requests
from pyquery import PyQuery as pq
from PIL import Image, ImageDraw, ImageFont
from StringIO import StringIO
import commands
import sys
import getopt
import os
import ctypes

# url of National Geographic - Photo of the Day site
BASE_URL = "http://photography.nationalgeographic.com/photography/photo-of-the-day"
# url where the downloaded image will be stored
IMAGE_FILE_URL_LINUX = "/tmp/ngwp.jpg"
IMAGE_FILE_URL_WINDOWS = "C://Windows//Temp//ngwp.jpg"
# url of a backup image which will be set in case of no Internet connection or other troubles
BACKUP_IMAGE_FILE_URL_LINUX = "/usr/share/backgrounds/linuxmint-rosa/jankaluza_electric_apple.jpg"
BACKUP_IMAGE_FILE_URL_WINDOWS = "C://Windows//Web//Wallpaper//Windows//img0.jpg"
# font used to write the caption of the image
FONT_URL_WINDOWS = "arial.ttf"
FONT_URL_LINUX = "/home/andrea/.fonts/Lato-Bold.ttf"
# FONT_URL_LINUX = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_SIZE = 14

# desktop environment and system
desktop_env = None


# START FUNCTION
def main (argv):

    global desktop_env

    # boolean to check if writing captions or not on the image
    write_caption = True
    the_url = ""
    the_backup_url = ""
    the_font_url = ""
    the_font_size = FONT_SIZE

    # set the desktop environment
    desktop_env  = get_desktop_environment()

    # set defaults
    if (desktop_env == "windows"):
        the_url = IMAGE_FILE_URL_WINDOWS
        the_backup_url = BACKUP_IMAGE_FILE_URL_WINDOWS
        the_font_url = FONT_URL_WINDOWS
    elif (desktop_env == "mac"):
        pass
    else:   # linux
        the_url = IMAGE_FILE_URL_LINUX
        the_backup_url = BACKUP_IMAGE_FILE_URL_LINUX
        the_font_url = FONT_URL_LINUX

    # parse arguments
    try:
        opts, args = getopt.getopt(argv[1:],'hns:b:f:d:', ['help', 'no_caption', 'image_location=', 'backup_image=', 'font=', 'font_size='])
    except getopt.GetoptError:
        print_help_msg(argv[0])
        sys.exit(-1)

    for opt, arg in opts:
        if (opt in ('-h', '--help')):
            print_help_msg(argv[0])
            sys.exit(0)
        elif (opt in ('-n', '--no_caption')):
            write_caption = False
        elif (opt in ('-s', '--image_location')):
            the_backup_url = arg
        elif (opt in ('-b', '--backup_image')):
            the_backup_url = arg
        elif (opt in ('-f', '--font')):
            the_font_url = arg
        elif (opt in ('-d', '--font_size')):
            if (arg.isdigit()):
                the_font_size = int(arg)
            else:
                print("> Font size is not a number.")
                sys.exit(-1)


    print("Setting the National Geographic, Photo of the Day wallpaper...")

    # get and set the image
    result = get_national_geographic(the_url, write_caption, the_font_url, the_font_size)
    if (result == 0): # ng image retrieved
        result = set_wallpaper(the_url)
        if (result != 0): # fail to set the ng image
            result = set_wallpaper(the_backup_url)
    else: # set the backup image
        set_wallpaper(the_backup_url)

def print_help_msg(app):
    print("Usage: %s [-nsbfdh]\n"\
    " -n | --no_caption\tSet wallpaper without write the caption on the image.\n"\
    " -s | --image_location\tUri (url + name.jpg) where save the temporary image.\n"\
    " -b | --backup_image\tUri (url + name.jpg) of the image to be used instead in case of troubles.\n"\
    " -f | --font\t\tUri (url + name.ttf) of the font to be used for the caption text.\n"\
    " -d | --font_size\tSize of the font.\n"\
    " -h | --help\t\tShow help message." % app)


# download the image from the site
def get_national_geographic(url, write_caption, font_url, font_size):

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

        i = Image.open(StringIO(image_raw))

        # edit the image (add caption)
        if (write_caption):
            font = ImageFont.truetype(font_url, font_size)
            draw = ImageDraw.Draw(i)
            width = i.size[0] - ((0.457 * font_size) * len(image_caption)) - 10
            height = i.size[1] - 29 - (82 * 0.8) - (font_size * 1.2)
            if ((width >= 0) and (height >= 0)):
                draw.text((width,height), image_caption, (255, 255, 255), font=font)

        # save the image
        i.save(url)

        return 0

    except (requests.exceptions.RequestException, requests.exceptions.ConnectionError, requests.exceptions.HTTPError, requests.exceptions.TooManyRedirects, requests.exceptions.Timeout):
        print("> Error: it seems that there are problems with the Internet connection")
        return -1
    except IOError:
        print("> Error: Input-Output error has been raised. Check permissions or the urls of the given paths")
        return -1

def set_wallpaper(url):

    global desktop_env

    if (desktop_env == "windows"):
        SPI_SETDESKWALLPAPER = 20
        ctypes.windll.user32.SystemParametersInfoA(SPI_SETDESKWALLPAPER, 0, url, 3)
        return 0
    elif (desktop_env == "mac"):
        pass
    else:   # linux
        SCHEMA = ""
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


# start the script
main(sys.argv)
