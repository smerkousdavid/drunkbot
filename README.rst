# drunkbot


### Intro
Drunk bot is a full python cross platform discord bot that has many capabilities even the ability to add your own.
Currently available options are youtube downloading (video and audio), playlist, audio web scrapers, image web scrapers,
playlist and song controls. Memes... random... uploading and downloading. Custom commands that you can add, some simple
math commands have been provided

**Now with simple command support**
Users who use drunkbot and add their own configured commands to Commands.txt
Without interfacing the discord.py api at all


## Installing

The installation of drunkbot can be easy for most users. Here is what you need to do.
*First* make sure that you have python3.5 installed on your machine. Some already have it
On others you might have to google how to install it. *Second* Also make sure you have pip installed.

**Linux users** Make sure you have (as discord.py says) these two packages installed
- libffi-dev (or `libffi-devel` on some systems)
- python<version>-dev (e.g. `python3.5-dev` for Python 3.5)


####Step 1

To install the stable version of drunkbot do this

...
python3.5 -m pip install -U drunkbot
...

If you want the (probably) unstable version

...
python3 -m pip install -U https://github.com/smerkousdavid/drunkbot/archive/master.zip#egg=drunkbot
...


####Step 2

Setup the bot with your account/application

If you already have a bot (application) and a token id just do

...
drunkbot --token 'TOKEN.ID'
...

This will automatically setup drunkbot to run with your client token id (This command wont start the sever keep reading)

If you **don't** have an application with a bot user

    1. Go here (login): https://discordapp.com/developers/applications/me
    2. Press new application
    3. Put a picture and name for the application (Description would be nice)
    4. Click "Create bot user" and click "Yes"
    5. Click "Show token on the bot"
    6. Copy and paste the token into the command above

####Step 3

Add the bot to a server

    1. Go here (login): https://discordapp.com/developers/applications/me
    2. Click on your previous application
    3. Copy and paste the client id into the url below (remove the < and > when pasting)
    4. https://discordapp.com/oauth2/authorize?client_id=<CLIENTID>&scope=bot&permissions=536083519
    5. Open that url (You should see a connect to discord window)
    6. Click select a server then click on your server
    7. Press the big blue authorize button
    8. You're done

## Usage

Now to actually run drunkbot

To see the available command line options run

...
drunkbot -h
...

Here is an example of starting the drunkbot server
With a startup message

...
drunkbot -s "I'm booted baby!"
...

####Getting started on discord

Send this message on the server the bot is located on

...
!help advanced
...

Example of me making a youtube search with drunk bot (Key words then what you want to do with the search)

...
!youtube karmin flex zone describe
...

Now if I wanted to play that song

...
!youtube karmin flex zone play
...

Annoyed of that song why don't you pause it...

...
!audio pause
...

Wait what do I have in stock on the sever

...
!audio list
...

Let me add something to it

...
!youtube pharrell marilyn download

or

!audio download william
...

Eww gross those sucked

...
!audio delete Pharrel all
...

I would just like to look at something now...

...
!random
...

Are you in the mood for french?

...
!youtube https://www.youtube.com/watch?v=5SM-nA5l2HU play
...

Trust me there are more commands i'm just having fun with these right now
Check out the !help for a current list of all commands

## License
This is licensed under General Public License (v3)
Look at the license file for more information

