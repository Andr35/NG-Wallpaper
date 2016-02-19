# NG Wallpaper
-----

A Python 3 script to set the National geographic's photos of the day as wallpaper on Linux distributions or Windows.

##### Dependencies:
- requests
- pyquery
- PIL (Pillow)

##### Usage:
```
./ng_wallpaper.py [-nh]
-n | --no_caption       Set wallpaper without write the caption on the image.
-s | --image_location   Uri (url + name.jpg) where save the temporary image.
-b | --backup_image     Uri (url + name.jpg) of the image to be used instead in case of troubles.
-f | --font             Uri (url + name.ttf) of the font to be used for the caption text.
-d | --font_size        Size of the font.
-h | --help             Show help message.

```
