# Cardiac Scraper

Hi, I made this as a research project. I can see it being useful if you want to modify it, so I wrote this guide on how to install and use this tool

## Installation

Getting this tool is reliant on a couple of other tools being installed. First install python from the [python](www.python.org) website. If you are running Linux (I do not run Arch btw), chances are it is already installed. Run `python --version` to see if it is already installed. You need python version 3.9 and up. I've only tested on 3.12 myself. 

Once python is installed, make sure you have `pip` installed by running `pip --version`. If it is not installed, run the following command to install `pip`:

`python -m ensurepip --upgrade`

Next download this repository using the download button provided on GitHubs site. You should be able to download as a zip file. Do that, then extract the files. 

Use the command line to navigate to wherever you extracted the files. Use the following commands to set up your environment:

`python -m venv .venv` in the **cardiac_scraper** folder. This creates a virtual environment for use in this project. Feel free to delete this after you are done using the scraper.

`pip install -t requirements.txt` to install any libraries that are not strictly default, i.e. the PRAW library used for interacting with Reddit's API.

## Usage

Usage is quite simple. Create a bot using Reddit's app registration service. You shouldn't need to pay anything and this tool accounts for Reddits TOS in terms of free accounts. All you need to do is: 

- copy the name, client id and client secret into the file named `praworiginal.ini`, 
- rename the file to `praw.ini`
- run the cardiac_scraper.py file with `python -m cardiac_scraper`

You'll get asked to log into your reddit account with the bot. This authenticates your bot with reddit, and allows you access to the site with user account access. This tool cannot edit posts or post on your behalf, which you can verify by reading the permissions of the tool. It requires permissions to search for posts on reddit. Feel free to edit the `cardiac_scraper.py` python file to search reddit with different search terms.

Once it is done, it should have created a few files.