# Chippy

Use ChatGPT in your Discord Server! 
Chippy v2.0 is currently built for deployment on fly.io.

### Usage

- Start a new chat with “@Chippy"
- Reply to posts to continue a conversation
- Chippy will reply in any channel
  - I would suggest making “chippy-text” and “chippy-images” channels and immediately globally muting them to save your notifications from being spammed.
  - Chippy also works inside threads, which are highly encouraged to keep things organized.

<img src="images/screenshots/chippy1.png" alt="Image description" width="290" height="300">

Chippy also formats code correctly:

<img src="images/screenshots/chippy2.png" alt="Image description" width="300" height="300">

Chippy supports image generation with DALL-E 2 or Stable Diffusion. This feature is disabled by default, as it can quickly become expensive on large servers. Start your message with "@chippy image of" to generate an image. If using Stable Diffusion, you can also specify a preset, such as "neon punk image of". You can list all available presets with "list presets"

<img src="images/screenshots/chippy3.png" alt="Image description" width="270" height="300">

### Advanced Usage

- Your first message can start with “you are” to set the context.
  - The default is "You are a helpful assistant."
  - This uses the "system" tag in the API, as opposed to the "user" or "assistant" tags.
  - Chippy won't respond to the context-setting message, so you will need to reply to it with the actual message you want answered.

<img src="images/screenshots/chippy4.png" alt="Image description" width="300" height="200">

### Privacy and Security

- Your Chippy will store a stripped-down verison of messages in a local Sqlite database. Ony message text and whether Chippy or a user sent it are stored. This is used for the ability to have conversation threads without recursively calling the Discord API, which is slow and will get the bot rate-limited. These messages are only accessable your Chippy instance.

### Setup

- Create a [Discord Bot](https://www.ionos.com/digitalguide/server/know-how/creating-discord-bot/)
  - Be sure to enable all Intents on the Bot tab and give it message reading and writing permissions when generating the join link.
  - The icon I used is in the repository as `images/chippy-logo.png`
  - After Chippy joins, change its role from "Chippy" to "RoleChippy" to prevent people from calling the role instead of the bot.
- Create an [OpenAI API Key](https://elephas.app/blog/how-to-create-openai-api-keys-cl5c4f21d281431po7k8fgyol0)
- Set up [flyctl](https://fly.io/docs/hands-on/install-flyctl/), the fly.io CLI tool
- Clone the repo
  - `git clone https://github.com/kahnpoint/chippy`
  - Copy `.env.example` to `.env` and fill in the values
  - In the `fly.toml`, be sure change the app name to something unique and the region to the one closest to you (list of regions [here](https://fly.io/docs/reference/regions/)). Do not change the `mount` values.
- Test it locally by running 
  - `python -m venv venv`
  - `source venv/bin/activate`
  - `pip install -r requirements.txt`
  - `python app.py`
- If everything works, run `flyctl deploy --remote-only` to deploy to fly.io. - Depending on usage, you may need to extend the volume's size with `fly volumes extend <volume-id> -s <size-in-gb>`.
- Chippy is live!

Not affiliated with OpenAI or Microsoft.