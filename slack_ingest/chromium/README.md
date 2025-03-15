# Chromium and chromedriver binaries to go here.

Download serverless-chrome special build from here:

https://github.com/adieuadieu/serverless-chrome/releases/download/v1.0.0-53/stable-headless-chromium-amazonlinux-2017-03.zip


Download chromedriver from here:
https://chromedriver.storage.googleapis.com/2.41/chromedriver_linux64.zip

Find the right version of chromedriver for the Chrome installed on your Mac here: https://sites.google.com/a/chromium.org/chromedriver/downloads

Name osx chromedriver binary chromedriver-osx to enable local development/testing

So should end up with files
```
chromium/headless-chromium
chromium/chromedriver
chromium/chromedriver-osx
```


If you really need updated chrome then can try some of the combos here, download the corresponding Chromedriver version from https://sites.google.com/a/chromium.org/chromedriver/downloads but have tried a fair few combinations and while they work fine on the local docker instance they error when uploaded to AWS. At least Chrome 69 and 86 aren't working even on AMI Lambda Python 3.6
https://github.com/adieuadieu/serverless-chrome/releases?after=v1.0.0-60
