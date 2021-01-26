# DailyWallpaper
## Python script that generates a desktop wallpaper featuring random Halo concept art, current weather, and joke

![Example Image](ExampleWallpaperImage.png)

### How To Use
1. Clone this repository
2. Install necessary site-packages
3. (optional) Update .bat file to link to your Python environment and the cloned repository's directory
4. (optional) Set the .bat file to run on startup ([Tutorial](https://www.sevenforums.com/tutorials/67503-task-create-run-program-startup-log.html))

### About The Project
I created this program to demonstrate webscraping using Python.

I like to have Halo themed wallpapers for my desktop but I do not want to have to download a lot of images to keep the wallpaper unique. The solution to this problem was to use Python to download a random Halo concept art image found on the [Halopedia](https://www.halopedia.org/) website. I could then dynamically set this image as my desktop's wallpaper. Whenever I log on to my computer, a batch script runs the Python script which updates the wallpaper. This way, I do not need to store a lot of images on my computer and the wallpaper is an image that I may have not seen before.

Logging on to my computer is one of the first things I do in the day so it would be nice to see what the weather is going to be like. I scrape the next 8 hours of weather for Portland from [Weather.com](https://weather.com/weather/hourbyhour/l/929a0a10df059030a591f46c408a7e6e022d06a80cdea1287444f02b92d9fd07) and display this info in a semi transparent box in the top right corner of the desktop wallpaper.

Finally, it is always good to start the day with a laugh so I scrape the daily joke from [ajokeaday.com](https://www.ajokeaday.com/) and display that underneath the weather.

In case I want to know more about the Halo image, weather, or joke, I save a text file to the desktop which has links to the website urls where I got the information.
