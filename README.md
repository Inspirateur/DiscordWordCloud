# DiscordWordCloud
A discord bot that generates a word cloud for each discord user.

The provided model used to generate the word cloud is dumb but fonctionnal, 
I encourage you to make your own ! (I personally use another one I cannot disclose)

# How to run it
- Clone the project wherever you want
- Install the requirements listed in `requirements.txt` with `pip`
- add a `token.txt` file at the root of the project
- go to https://discordapp.com/developers/applications/ create your app, add a User Bot to it and paste its Client ID in `token.txt`
- run the `main.py` with Python 3.5+!

If you wish to invite my version of this bot on your server PM `Inspi#8989` on Discord

# Features
everyone:
- `;cloud (<user(s)>)` to generate your word cloud, you can also tag users to generate their clouds
- `;word <word>` to get a list of the top \<word> users in your server

Requires manage channel permission:
- `;ignore <channel(s)>` to make make the bot ignore <channel(s)> while training the model
- `;listen <channel(s)>` to make make the bot listen to <channel(s)> while training the model 
(by defaults the bot read all the channel it has read access to)

Please note that this project is still in development, 
some features like emoji display, real time training, are not implemented yet.

*P.S.: for now there's no real time training, so the bot will automatically train when starting and save its model after training. If a save of its model is present in `WordCloudModel/your_model_save.json` it will load it instead of training, if you don't want that just delete the save before starting the bot.*
