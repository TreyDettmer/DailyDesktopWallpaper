"""
This program updates the desktop wallpaper/background to be a random image of Halo concept art found online.
The background image is overlaid with the current weather forecast for Portland Oregon as well as a joke found online.

Author: Trey Dettmer
"""

import ctypes
import requests
import cv2
from lxml import html
import pandas as pd
from bs4 import BeautifulSoup
import random
import numpy as np
import os
from PIL import Image, ImageDraw, ImageFont
from screeninfo import get_monitors

WEATHER_WIDTH = 240
WEATHER_HEIGHT = 320
JOKE_WIDTH = 240
JOKE_HEIGHT = 300
FONT = cv2.FONT_HERSHEY_SCRIPT_COMPLEX
try:
    DISPLAY_WIDTH = get_monitors()[0].width
    DISPLAY_HEIGHT = get_monitors()[0].height
except:
    DISPLAY_HEIGHT = 1080
    DISPLAY_WIDTH = 1920
LINK_TO_BACKGROUND = ""
LINK_TO_JOKE = ""
LINK_TO_WEATHER = ""

""" Fetches and returns Halo concept art from online """


def get_background_image():
    global LINK_TO_BACKGROUND

    page = requests.get("https://www.halopedia.org/Category:Concept_art")
    soup = BeautifulSoup(page.content, 'html.parser')

    # get the categories of concept art
    categories = soup.find_all(class_="mw-category-group")

    # remove the first category since it's the Halo books
    categories.pop(0)

    # choose random category
    chosenCategory = random.choice(categories)

    subcategories = chosenCategory.find_all("li")
    chosenSubCategory = random.choice(subcategories)

    subCategoryText = chosenSubCategory.find("a")["href"]

    artPageLink = "https://www.halopedia.org" + subCategoryText
    artPage = requests.get(artPageLink)
    soup = BeautifulSoup(artPage.content, 'html.parser')

    allImages = soup.find_all(class_="thumb")
    allImages = ["https://www.halopedia.org" + wrapper.find("a")["href"] for wrapper in allImages]

    chosenImageIndex = random.randrange(0, len(allImages))
    chosenImageBasePage = requests.get(allImages[chosenImageIndex])
    soup = BeautifulSoup(chosenImageBasePage.content, 'html.parser')
    imageLink = "https://www.halopedia.org" + soup.find(class_="fullMedia").find("a")["href"]
    chosenImage = Image.open(requests.get(imageLink, stream=True).raw)

    chosenImage = chosenImage.convert('RGB')
    chosenImage = np.array(chosenImage)
    LINK_TO_BACKGROUND = allImages[chosenImageIndex]
    # Convert RGB to BGR
    chosenImage = chosenImage[:, :, ::-1].copy()

    return chosenImage


""" Fetches and returns a joke from online """


def get_joke():
    global LINK_TO_JOKE

    page = requests.get("https://www.ajokeaday.com/")
    LINK_TO_JOKE = "https://www.ajokeaday.com/"
    tree = html.fromstring(page.content)
    jokeBase = tree.xpath("//div[@class='jd-body jubilat']/p/text()")
    joke = [j.rstrip('\r') for j in jokeBase]
    while "" in joke:
        joke.remove("")
    joke = " ".join(joke)

    return joke


""" Fetches weather info and returns a Pandas dataframe with the Portland weather forecast for the next 8 hours"""


def get_forcast_info():
    global LINK_TO_WEATHER
    forecasts = []

    # get html content from weather.com
    page = requests.get(
        "https://weather.com/weather/hourbyhour/l/929a0a10df059030a591f46c408a7e6e022d06a80cdea1287444f02b92d9fd07")
    LINK_TO_WEATHER = "https://weather.com/weather/hourbyhour/l/929a0a10df059030a591f46c408a7e6e022d06a80cdea1287444f02b92d9fd07"
    soup = BeautifulSoup(page.content, 'html.parser')
    hourlyForecasts = soup.select("details[class^=DaypartDetails--DayPartDetail]")

    for forecast in hourlyForecasts:

        # get the forecast info for this hour
        timeOfDay = forecast.find(class_="DetailsSummary--daypartName--1Mebr").text.replace(" ", "")
        temperature = forecast.find(class_="DetailsSummary--tempValue--RcZzi").text
        description = forecast.find(class_="DetailsSummary--extendedData--aaFeV").text
        percentChance = forecast.select('span[data-testid="PercentageValue"]')[0].text

        # add this hour's forecast to the list of forecasts
        forecasts.append({'time': timeOfDay, 'temp': temperature, 'desc': description, 'perc': percentChance})

        # limit to 8 hours of weather
        if len(forecasts) == 8:
            break;
    df = pd.DataFrame(forecasts)

    return df


""" Resizes given concept art so that it will fit in the display. Returns desktop background with concept art applied"""


def create_background_image(cArt):
    displayAspectRatio = DISPLAY_WIDTH / DISPLAY_HEIGHT
    cArtAspectRatio = cArt.shape[1] / cArt.shape[0]

    if cArtAspectRatio > displayAspectRatio:  # wider than display
        scaleFactor = DISPLAY_WIDTH / cArt.shape[1]
        newHeight = int(cArt.shape[0] * scaleFactor)
        cArt = cv2.resize(cArt, (DISPLAY_WIDTH, newHeight))
        startRow = int(DISPLAY_HEIGHT / 2 - cArt.shape[0] / 2)
        desktopBackground[startRow:startRow + newHeight, 0:DISPLAY_WIDTH] = cArt
    elif cArtAspectRatio < displayAspectRatio:  # taller than display
        scaleFactor = DISPLAY_HEIGHT / cArt.shape[0]
        newWidth = int(cArt.shape[1] * scaleFactor)
        cArt = cv2.resize(cArt, (newWidth, DISPLAY_HEIGHT))
        startCol = int(DISPLAY_WIDTH / 2 - cArt.shape[1] / 2)
        desktopBackground[0:DISPLAY_HEIGHT, startCol:startCol + newWidth] = cArt
    else:  # equal to display aspect ratio
        cArt = cv2.resize(cArt, (DISPLAY_WIDTH, DISPLAY_HEIGHT))
        desktopBackground[:, :] = cArt

    return desktopBackground


""" Draws the weather info on the weather image """


def create_weather_overlay():
    forecastsDf = get_forcast_info()
    pilWeatherImage = Image.fromarray(weatherImage)
    pilDrawImage = ImageDraw.Draw(pilWeatherImage)
    trueFont = ImageFont.truetype("impact.ttf", 20)
    rowSize = 31
    colSize = 55

    retVal, _ = cv2.getTextSize("Weather", FONT, .75, 1)
    weatherTitleXpos = 120 - int(retVal[0] / 2)

    pilDrawImage.text((weatherTitleXpos, 20), "Weather", font=trueFont, anchor="ls")
    trueFont = ImageFont.truetype("impact.ttf", 16)
    pilDrawImage.text((0, 45), " Time  Temp        Desc                       Rain", font=trueFont, anchor="ls")
    pilDrawImage.line([(0, 44), (WEATHER_WIDTH, 44)])

    headerHeight = 70
    for row in range(8):
        pilDrawImage.text((5, headerHeight + rowSize * row), forecastsDf.loc[row, "time"], font=trueFont, anchor="ls")
        pilDrawImage.text((colSize, headerHeight + rowSize * row), forecastsDf.loc[row, "temp"], font=trueFont,
                          anchor="ls")
        pilDrawImage.text((colSize * 2 - 20, headerHeight + rowSize * row), forecastsDf.loc[row, "desc"], font=trueFont,
                          anchor="ls")
        pilDrawImage.text((colSize * 3 + 40, headerHeight + rowSize * row), forecastsDf.loc[row, "perc"], font=trueFont,
                          anchor="ls")

    img = cv2.cvtColor(np.array(pilWeatherImage), cv2.COLOR_RGB2BGR)

    return img


""" Makes given image have a semi-transparent background, then applies the image to the returned desktop background """


def add_image_overlay(imgToOverlay, xCoord, yCoord):
    grayImageToOverlay = cv2.cvtColor(imgToOverlay, cv2.COLOR_BGR2GRAY)
    ret, mask = cv2.threshold(grayImageToOverlay, 220, 255, cv2.THRESH_BINARY)
    mask_inv = cv2.bitwise_not(mask)

    imgToOverlayText = cv2.bitwise_and(imgToOverlay, imgToOverlay, mask=mask)

    # add semi-transparent black background
    desktopBackgroundCopy = desktopBackground.copy()
    desktopBackgroundCopy[yCoord:yCoord + imgToOverlay.shape[0], xCoord:DISPLAY_WIDTH] = imgToOverlay
    cv2.addWeighted(desktopBackgroundCopy, .5, desktopBackground, .5, 0, desktopBackground)

    # add white text
    roi = desktopBackground[yCoord:yCoord + imgToOverlay.shape[0], xCoord:DISPLAY_WIDTH]
    desktImgBg = cv2.bitwise_and(roi, roi, mask=mask_inv)
    dst = cv2.add(desktImgBg, imgToOverlayText)
    desktopBackground[yCoord:yCoord + imgToOverlay.shape[0], xCoord:DISPLAY_WIDTH] = dst

    return desktopBackground


""" Draws the joke on the joke image """


def create_joke_overlay():
    # convert cv2 image to PIL image so that we can use impact font
    pilJokeImage = Image.fromarray(jokeImage)
    pilDrawImage = ImageDraw.Draw(pilJokeImage)
    trueFont = ImageFont.truetype("impact.ttf", 20)

    retVal, _ = cv2.getTextSize("Joke", FONT, .75, 1)
    jokeTitleXpos = JOKE_WIDTH / 2 - int(retVal[0] / 2)
    pilDrawImage.text((jokeTitleXpos, 20), "Joke", font=trueFont, anchor="ls")

    joke = get_joke()

    jokeTextSize, _ = cv2.getTextSize(joke, FONT, .5, 1)

    jokeWords = joke.split()
    jokeLines = []
    previousWords = []
    # Manually make the joke text fit into the joke image
    for i in range(len(jokeWords)):
        if len(previousWords) > 0:
            temp = ' '.join(previousWords) + " " + jokeWords[i]
            tempSize, _ = cv2.getTextSize(temp, FONT, .5, 1)
            if tempSize[0] > JOKE_WIDTH:
                jokeLines.append(' '.join(previousWords))
                previousWords = []
        previousWords.append(jokeWords[i])
    jokeLines.append(' '.join(previousWords))

    trueFont = ImageFont.truetype("impact.ttf", 16)
    for i in range(len(jokeLines)):
        pilDrawImage.text((10, 45 + 25 * i), jokeLines[i], font=trueFont, anchor="ls")

    img = cv2.cvtColor(np.array(pilJokeImage), cv2.COLOR_RGB2BGR)
    # crop the new image to fit the text
    lastLineYpos = 45 + 25 * (len(jokeLines) - 1) + 25
    croppedImage = img[0:lastLineYpos, :]

    return croppedImage


# add concept art image
conceptArt = get_background_image()
desktopBackground = np.zeros((DISPLAY_HEIGHT, DISPLAY_WIDTH, 3), np.uint8)
desktopBackground = create_background_image(conceptArt)

# add weather
weatherImage = np.zeros((WEATHER_HEIGHT, WEATHER_WIDTH, 3), np.uint8)
weatherImage = create_weather_overlay()
desktopBackground = add_image_overlay(weatherImage, DISPLAY_WIDTH - weatherImage.shape[1], 0)

# add joke
jokeImage = np.zeros((JOKE_HEIGHT, JOKE_WIDTH, 3), np.uint8)
jokeImage = create_joke_overlay()
desktopBackground = add_image_overlay(jokeImage, DISPLAY_WIDTH - jokeImage.shape[1], weatherImage.shape[0])

# save the new desktop background
cv2.imwrite("desktop_background.jpg", desktopBackground)
dir_path = os.path.dirname(os.path.realpath(__file__))
dir_path = os.path.join(dir_path, "desktop_background.jpg")
ctypes.windll.user32.SystemParametersInfoW(20, 0, dir_path, 3);

# write the info about the desktop background into a text file saved on the Desktop
infoPath = os.path.join(os.path.join(os.path.join(os.path.join(os.environ['USERPROFILE']), 'OneDrive'), 'Desktop'),
                        'BackgroundInfo.txt')
f = open(infoPath, "w")
f.write("Image: " + LINK_TO_BACKGROUND + "\n")
f.write("Weather: " + LINK_TO_WEATHER + "\n")
f.write("Joke: " + LINK_TO_JOKE + "\n")
f.close()
