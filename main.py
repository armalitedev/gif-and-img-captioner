from PIL import Image, ImageDraw, ImageFilter, ImageColor, ImageFont, ImageSequence
import textwrap
import io
import requests
import wget
import os
import json
import urllib.request, urllib.parse, urllib.error
import pprint
import imageio
from time import sleep
from random import randint
from icrawler.builtin import GoogleImageCrawler
import shutil

#frames[0].save("aa.gif", save_all=True, append_images=frames[1:], optimize=False, duration=40, loop=0)
#synchronize_gifs_out("cat.gif", "out.gif")

def caption_image_out(im, message, font_path):
  """ Returns captioned image for gifs use
  """
  im = im.convert("RGB")
  image = im.copy()
  x, y = image.size
  copy = image.copy()
  font = ImageFont.truetype(font_path, x // 15)
  draw = ImageDraw.Draw(image)
  image_width, image_height = image.size
  y_text = int(y * 0.04)
  oldlines = textwrap.wrap(message, width=28, break_on_hyphens=True)
  lines=[]
  for p in range(len(oldlines)):
    oldlines[p]=oldlines[p].split("|")
  for p in oldlines:
    if type(p)==str:
      lines.append(p)
    else:
      for q in p:
        lines.append(q)
  chosen = False
  for line in lines:
    if chosen == False:
      line_width, line_height = font.getsize(line)
      line_height = line_height + int(line_height * 0.40)
      line_width = line_width - int(line_width * 0.10)
    chosen = True
    draw.text((x / 2, y_text), line, font=font, fill=(0, 0, 0), anchor="ma")
    y_text += line_height

  frame = Image.new("RGB",
                    (x, int(y * 0.04) + y + y_text + int(line_height * 0.40)),
                    (255, 255, 255))
  frame.paste(copy, (0, y_text + int(line_height * 0.40) + int(y * 0.04)))
  frame_draw = ImageDraw.Draw(frame)
  y_text = int(line_height * 0.30) + int(y * 0.04)
  for line in lines:
    frame_draw.text((x / 2, y_text),
                    line,
                    font=font,
                    fill=(0, 0, 0),
                    anchor="ma")
    y_text += line_height
  return frame


def synchronize_gifs_out(gif1_path, gif2_path):
  """ Synchronize the fps of two gifs
    """
  gif1_fps = 1000 / Image.open(gif1_path).info['duration']
  gif = imageio.mimread(gif2_path)
  imageio.mimsave(gif2_path, gif, fps=gif1_fps)


class Meme:

  def __init__(self, path):
    self.img = Image.open(path)
    self.x = Image.open(path).size[0]
    self.y = Image.open(path).size[1]
    self.size = Image.open(path).size

  def caption_image(self, message, font_path):
    """ Returns captioned image
    """
    self.img = self.img.convert("RGB")
    image = self.img.copy()
    copy = image.copy()
    font = ImageFont.truetype(font_path, self.x // 15)
    draw = ImageDraw.Draw(image)
    image_width, image_height = image.size
    y_text = int(self.y * 0.04)
    oldlines = textwrap.wrap(message, width=28, break_on_hyphens=True)
    lines=[]
    for x in range(len(oldlines)):
       oldlines[x]=oldlines[x].split("|")
    for x in oldlines:
      for y in x:
        lines.append(y)
    chosen = False
    for line in lines:
      if chosen == False:
        line_width, line_height = font.getsize(line)
        line_height = line_height + int(line_height * 0.40)
        line_width = line_width - int(line_width * 0.10)
      chosen = True
      draw.text((self.x / 2, y_text),
                line,
                font=font,
                fill=(0, 0, 0),
                anchor="ma")
      y_text += line_height

    frame = Image.new(
      "RGB",
      (self.x, int(self.y * 0.04) + self.y + y_text + int(line_height * 0.40)),
      (255, 255, 255))
    frame.paste(copy,
                (0, y_text + int(line_height * 0.40) + int(self.y * 0.04)))
    frame_draw = ImageDraw.Draw(frame)
    y_text = int(line_height * 0.30) + int(self.y * 0.04)
    for line in lines:
      frame_draw.text((self.x / 2, y_text),
                      line,
                      font=font,
                      fill=(0, 0, 0),
                      anchor="ma")
      y_text += line_height
    return frame

  def caption_gif(self, message, font_path):
    """ Returns frames of captioned gif
    """
    im = self.img
    frames = []
    # Loop over each frame in the animated image
    for frame in ImageSequence.Iterator(im):
      captioned = caption_image_out(frame, message, font_path)
      b = io.BytesIO()
      captioned.save(b, format="GIF")
      captioned = Image.open(b)

      # Then append the single frame image to a list of frames
      frames.append(captioned)
    return frames

def get_gifurl(searchTerm):
  """ Fetches gif url from tenor
  """
  # set the apikey and limit
  apikey = "api here"  # test value
  lmt = 1
  ckey = "my_test_app"
  
  """returns the tenor url of a term
    """
  r = requests.get(
    "https://tenor.googleapis.com/v2/search?q=%s&key=%s&client_key=%s&limit=%s"
    % (searchTerm, apikey, ckey, lmt))
  data = r.json()

  # see urls for all GIFs
  for result in data['results']:
    for x in result["media_formats"].keys():
      if x == "gif":
        return result["media_formats"][x]["url"]

def download_gif(gifurl):
  e=str(randint(999999999999,99999999999999))+".gif"
  wget.download(gifurl, e)
  return e

def tenor(term,msg):
  """ Download and caption from tenor
  """
  if msg=="":
    g=get_gifurl(term)
    e=download_gif(g)
    shutil.move(e, "pics/"+e)
    meme=Meme("pics/"+e)
    return "pics/"+e
  g=get_gifurl(term)
  e=download_gif(g)
  meme=Meme(e)
  frames=meme.caption_gif(msg,
    "Archivo-Bold.ttf")
  frames[0].save("pics/"+e, save_all=True, append_images=frames[1:], optimize=False, duration=40, loop=0)
  synchronize_gifs_out(e, "pics/"+e)
  os.remove(e)
  print(e)
  return "pics/"+e

def google(searchterm,msg):
  """ Download and caption from google images
  """
  if msg=="":
    google_crawler = GoogleImageCrawler()
    google_crawler.crawl(keyword=searchterm, max_num=10)
    e=str(randint(999999999999,99999999999999))+".jpg"
    meme=Meme("images/000001.jpg")
    meme.img.save("pics/"+e)
    shutil.rmtree("images") 
    return "pics/"+e
  google_crawler = GoogleImageCrawler()
  google_crawler.crawl(keyword=searchterm, max_num=1)
  e=str(randint(999999999999,99999999999999))+".jpg"
  meme=Meme("images/000001.jpg")
  meme.caption_image(msg,
    "Archivo-Bold.ttf").save("pics/"+e)
  shutil.rmtree("images") 
  return "pics/"+e
