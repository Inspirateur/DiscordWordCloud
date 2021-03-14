# DiscordWordCloud
A Python 3.9 discord bot that generates a word cloud (now with emojis !) for each discord user.

## How to run it
- Clone the project wherever you want
- Install Python 3.9 from https://www.python.org/ (you can probably use an older version too)
- Install the requirements listed in `requirements.txt` with `pip`
  - use `python -m pip install -r requirements.txt` at the root of the project
  - consult this guide if you need help with pip https://packaging.python.org/tutorials/installing-packages/
- add a `token.txt` file at the root of the project
- go to https://discordapp.com/developers/applications/ create your app, add a User Bot to it and paste its Token in `token.txt`
- you will also need to enable `SERVER MEMBERS INTENT` in the bot tab  
- invite the bot on your Discord Server https://discordpy.readthedocs.io/en/latest/discord.html#inviting-your-bot
- run `main.py` with Python 3.9

And it should run !


If you got any questions about this project, feel free to DM `Inspi#8989` on Discord.

## Features
- `;load (days)` use this to load messages up to x days on your server 
- `;cloud` to generate your word cloud, you can also tag someone in the command to generate their word cloud
- `;emojis` to get the custom emojis usage of the server

## Pictures
![](https://github.com/Inspirateur/DiscordWordCloud/blob/master/screenshots/emojis.png)
<img float="right" src="https://github.com/Inspirateur/DiscordWordCloud/blob/master/screenshots/cloud1.png">
<img float="right" src="https://github.com/Inspirateur/DiscordWordCloud/blob/master/screenshots/cloud2.png">

## How it works

Here's a step by step of how the bot makes a wordcloud:
- after `;load` 
  - for each word `w` and user `u`, compute `p(w|u)`, the probability of `u` writing `w` *(this data is separated between servers)*
- after `;cloud` 
  - for each word `w` and the user `u` for which the cloud is, compute `p(w|u)/p(w)`, this quantifies how much `u` *favors* `w` compared to everyone else
  - uses the WordCloud lib to make a word cloud image, scaling the words in proportion to their scores (they are placed randomly)
  
Some notes regarding this model:
- This model as-is would be filled with typos, bits of url and words that have only been written by `u` because `p(w|u)/p(w)` would be high; to counter this, a value `α` is added to every `p(w|u)` as if each user had at least an `α` probability of writing any word.
  This regularisation has the downside of putting some words that were never written by `u` in the word cloud. 
- A strong point of this model is that it works in any language and stop-words such as *and, the, a, etc.*
are often excluded because they are not favored by anyone in particular.
- One limitation of the model is that it does not handle expressions bigger than a single word or emoji.

The code is written so that implementing a new model is easy, by subclassing `WCModel` in `wcmodel.py`, 
and importing your custom class instead of `WCBaseline` in `main.py` ! 

## Powered by:

- discord.py: https://github.com/Rapptz/discord.py
- WordCloud: https://github.com/amueller/word_cloud
- Twemoji: https://twemoji.twitter.com/
