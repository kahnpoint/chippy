
Chippy: ChatGPT in Discord

Start a chat with “@Chippy" and reply to posts to continue a conversation. Chippy will reply in any channel, but I would suggest making “chippy-text” and “chippy-images” channels. (and muting them) Chippy also works inside threads, which is highly recommended.
 
Chippy also formats code correctly:


Chippy supports image generation (uses DALL-E 2, disabled by default)


Advanced Usage
Your first message can start with “you are” to set the context (“system” tag in the API)

Setup
Create a Discord bot
https://www.ionos.com/digitalguide/server/know-how/creating-discord-bot/
be sure to enable the Message Content Intent on the Bot tab and adequate text permissions when it joins. 
The icon I used is in the repository as ```chippy-logo.png```
Create an OpenAI API Key
https://elephas.app/blog/how-to-create-openai-api-keys-cl5c4f21d281431po7k8fgyol0
Get a server
Any virtual machine will work, I have mine running in a Google Cloud compute unit.
Set up Chippy
install the python packages (make sure openai is at least 0.27)
```pip install openai discord.py requests```
navigate to the folder where you want chippy to be
```mkdir chippy```
```cd chippy```
put the app.py file from this repository into the folder
create a folder called images, which is where generated images will be saved, if enabled
```mkdir images```
open app.py to input your keys and make sure all the settings are what you want
```sudo nano app.py```
run it with
```nohup python3 app.py &```
