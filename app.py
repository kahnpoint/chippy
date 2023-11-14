# Chippy v2.0
# By kahnpoint (Adam Kahn)
# https://g%%%ithub.com/kahnpoint/chippy
# Released under the MIT License

import discord
import openai
import requests
import sqlite3
import time
import os
from dotenv import load_dotenv
import base64


mount_point = "./chippy_data"

# load environment variables
# use development environment if it exists
if os.path.exists("./workbooks/.env"):
    load_dotenv("./workbooks/.env")
else:
    load_dotenv()
env = os.environ


# set up discord
intents = discord.Intents.all()
client = discord.Client(intents=intents)

# set up openai
openai.api_key = env["OPENAI_TOKEN"]

IMAGE_PROMPT = "image of"
STABILITY_STYLE_PRESETS = [
    "3d-model",
    "analog-film",
    "anime",
    "cinematic",
    "comic-book",
    "digital-art",
    "enhance",
    "fantasy-art",
    "isometric",
    "line-art",
    "low-poly",
    "modeling-compound",
    "neon-punk",
    "origami",
    "photographic",
    "pixel-art",
    "tile-texture",
]

# CLASSES


# this class represents a database connection
class Database:
    # instatiate self and create connection
    def __init__(self, database_name):
        os.makedirs(mount_point, exist_ok=True)
        self.database_name = mount_point + "/" + database_name + ".db"
        self.conn = sqlite3.connect(self.database_name)
        self.cursor = self.conn.cursor()

    # close connection
    def close(self):
        self.conn.commit()
        self.conn.close()


# this class holds functions for storing messages in the database


class SqlUtils:
    def __init__():
        None

    # create "messages" table
    async def create_database():
        db = Database(env["DB_NAME"])
        db.cursor.execute(
            """
                    CREATE TABLE IF NOT EXISTS messages
                    (
                        message_id INTEGER PRIMARY KEY,
                        parent_id INTEGER,
                        role TEXT,
                        message TEXT
                    )
                    """
        )
        db.close()

    # drop messages table (unused)
    async def drop_table(table_name):
        db = Database(env["DB_NAME"])
        db.cursor.execute(f"""DROP TABLE IF EXISTS {table_name}""")
        db.close()

    # insert a single message into messages
    async def enter_message(message_id, parent_id, role, message):
        message = message.replace('"', "'")
        db = Database(env["DB_NAME"])
        db.cursor.execute(
            f"""INSERT OR REPLACE INTO messages 
                    (message_id, parent_id, role, message)
                    VALUES({message_id}, {parent_id}, "{role}", "{message}")
                    """
        )
        db.close()

    # get a single message from messages
    async def get_message(message_id):
        db = Database(env["DB_NAME"])
        db.cursor.execute(
            f"""
                    SELECT * FROM messages 
                    WHERE message_id = {message_id}
                    """
        )
        response = db.cursor.fetchone()
        db.close()
        return response

    # get a thread of all parents from messages
    async def get_thread(message_id):
        messages = []

        # get info for self
        row = await SqlUtils.get_message(message_id)
        messages.append(row)

        # loop through parents
        while row[1] != None:
            message_id = row[1]
            row = await SqlUtils.get_message(message_id)
            messages.append(row)

        # return reversed (chronological) string
        return messages[::-1]


# COMPLETION FUNCTIONS (OpenAI API interfaces)


# returns chat completion (ChatGPT)
async def chat_completion(messages):
    response = None
    try:
        response = openai.chat.completions.create(
            model=env["CHAT_MODEL"], messages=messages
        )
        return response.choices[0].message.content
    except Exception as e:
        if response:
            return str(e) + str(response)
        else:
            return str(e)


# returns text completion (old model, deprecated)
def text_completion(message, max_tokens=2048):
    response = openai.Completion.create(
        model=env["TEXT_MODEL"], prompt=message, max_tokens=max_tokens
    )
    return response["choices"][0]["text"]


# openai DALLE2
# returns a url of an image
def image_completion(message, resolution=str(env["IMAGE_SIZE"])):
    response = openai.Image.create(
        prompt=message,
        n=1,
        size=f"{resolution}x{resolution}",
    )
    return response["data"][0]["url"]


# stabillity ai
# returns a filepath of an image
def generate_stability_image(text_prompt):
    IMAGE_PROMPT = "image of"
    IMAGE_PROMPTS = [f"{i.replace('-', ' ')}" for i in STABILITY_STYLE_PRESETS]

    def get_image_preset(text_prompt):
        # returns a tuple of image preset and image prompt
        if text_prompt.startswith(IMAGE_PROMPT):
            return None, (text_prompt.split(IMAGE_PROMPT)[1].strip())
        for i in IMAGE_PROMPTS:
            if text_prompt.startswith(i):
                return i.replace(" ", "-"), (text_prompt.split(IMAGE_PROMPT)[1].strip())

    style_preset, image_prompt = get_image_preset(text_prompt)
    print(style_preset, image_prompt)
    json = {
        "text_prompts": [{"text": image_prompt}],
        "cfg_scale": 7,
        # "clip_guidance_preset": "FAST_BLUE",
        "height": 512,
        "width": 512,
        "samples": 1,
        "steps": 30,
    }
    if style_preset:
        json["style_preset"] = style_preset

    engine_id = "stable-diffusion-xl-beta-v2-2-2"
    # engine_id = "stable-diffusion-v1-5"
    api_host = os.getenv("API_HOST", "https://api.stability.ai")
    api_key = env["STABILITY_TOKEN"]

    if api_key is None:
        raise Exception("Missing Stability API key.")

    response = requests.post(
        f"{api_host}/v1/generation/{engine_id}/text-to-image",
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        json=json,
    )

    if response.status_code != 200:
        raise Exception("Non-200 response: " + str(response.text))

    data = response.json()

    filename = "".join(
        [
            letter
            for letter in text_prompt.lower().replace(" ", "_")
            if letter.isalnum() or letter == "_"
        ]
    )[:100]

    output_filename = f"./images/{filename}.png"

    for i, image in enumerate(data["artifacts"]):
        with open(output_filename, "wb") as f:
            f.write(base64.b64decode(image["base64"]))

    return output_filename


# returns a generated image as a file
async def get_image(prompt):
    if env["USE_STABILITY"]:
        output_filename = generate_stability_image(prompt)
    else:
        # image prompt
        completion_url = image_completion(prompt)

        # format the filename to be the first 100 characters of the prompt
        filename = "".join(
            [
                letter
                for letter in prompt.lower().replace(" ", "_")
                if letter.isalnum() or letter == "_"
            ]
        )[:100]

        # get and save image
        response = requests.get(completion_url)
        output_filename = f"{mount_point}/images/{filename}.png"
        if env["SAVE_IMAGES"]:
          with open(output_filename, "wb") as f:
              f.write(response.content)

    with open(output_filename, "rb") as f:
        file = discord.File(f, filename=f"{output_filename}.png")
    return file


# DISCORD FUNCTIONS


# strip @chippy out of the initial message
async def message_to_prompt(message):
    # look for user tag
    if message.content.strip().startswith("<") and ">" in message.content:
        # strip first user out
        prompt = message.content[message.content.index(">") + 1 :].strip()
    else:
        # return original message
        prompt = message.content
    return prompt


# get a message's parent from discord
async def get_parent_discord(message):
    # check to see if message has a parent
    if message.reference is not None:
        # Retrieve the parent message using the reference
        parent = await message.channel.fetch_message(message.reference.message_id)
    else:
        parent = None
    return parent


# get parents from local sqlite database
async def get_parents_locally(message):
    # get thread
    thread = await SqlUtils.get_thread(message.id)

    if thread:
        # format thread as messages for OpenAI
        messages = [{"role": i[2], "content": i[3]} for i in thread]
        return messages
    else:
        return []


# get all the parent messages by recursively calling discord (deprecated)
async def get_parents_discord(message):
    parents = []
    current_message = message

    # loop while there still exist parents
    while current_message.reference is not None:
        # Retrieve the parent message using the reference
        parent_message = await get_parent_discord(current_message)

        # Add the parent message to the list
        parents.append(parent_message)

        # Traverse up the message tree
        current_message = parent_message

        # prevent getting rate limited
        time.sleep(10 / 1000)

    # reverse order for the formatter
    parents = parents[::-1]
    parents.append(message)
    return parents


# format the discord messages for ChatGPT API (deprecated)
async def format_parents_discord(messages):
    messages_output = []

    # loop through messages and format for OpenAI API
    for m in messages:
        prompt = await message_to_prompt(m)

        if m.author.name.lower() == env["BOT_NAME"].lower():
            role = "assistant"
        else:
            role = "user"

        messages_output.append({"role": role, "content": prompt})

    # check to see if there is a user-set context
    if messages_output[0]["role"].lower() != "system":
        messages_output = [
            {"role": "system", "content": env["DEFAULT_CONTEXT"]}
        ] + messages_output

    if env["DEBUG"]:
        for m in messages_output:
            print(m)

    return messages_output


# traverse the tree up to the original parent


async def get_thread(message):
    if env["STORE_LOCALLY"]:
        return await get_parents_locally(message)
    else:
        parents = await get_parents_discord(message)
        return await format_parents_discord(parents)


# store message in local database


async def store_locally(message):
    # save " as "" for storing in Sqlite
    message.content = message.content.replace('"', "'")

    # local variables
    author = message.author
    reference = message.reference
    prompt = await message_to_prompt(message)

    # if no parent, set to NULL (Sqlite's version of None)
    if reference is None:
        reference = "NULL"
    else:
        reference = message.reference.message_id

    # if message is context-setting set role as "system"
    if prompt.lower().startswith("you are"):
        author = "system"

    # if bot sent message set role as "assistant"
    elif message.author == client.user:
        author = "assistant"

    # if user sent message set role as "user"
    else:
        author = "user"

    if env["DEBUG"]:
        print(message.id, message.reference, message.author, prompt)

    # wait for the entry to be entered into sqlite
    await SqlUtils.enter_message(message.id, reference, author, prompt)


# DISCORD BOT FUNCTIONS


# standard discord bot startup function
@client.event
async def on_ready():
    print(f"{client.user.display_name} is online")
    await SqlUtils.create_database()
    # set default context
    await SqlUtils.enter_message(0, "NULL", "system", env["DEFAULT_CONTEXT"])


def is_image_prompt(text_prompt):
    # returns whether or not the prompt is an image prompt
    if text_prompt.startswith(IMAGE_PROMPT):
        return True
    if IMAGE_PROMPT in text_prompt:
        for i in [i.replace("-", " ") for i in STABILITY_STYLE_PRESETS]:
            if text_prompt.startswith(i):
                return True
    return False


# on message event
@client.event
async def on_message(message: discord.Message):
    # print recieved messages
    print("recieved", message.content)

    # get prompt from message
    prompt = await message_to_prompt(message)

    if prompt == "list presets":
        await message.reply(
            "```"
            + ", ".join([i.replace("-", " ") for i in STABILITY_STYLE_PRESETS])
            + "```"
        )
        return

    # test to see if bot is mentioned (for images)
    if client.user in message.mentions:
        # see if images are enabled
        if is_image_prompt(prompt) and env["ALLOW_IMAGES"]:
            # get image
            file = await get_image(prompt)
            # send message
            await message.reply(prompt, file=file)
            return
        if env["STORE_LOCALLY"]:
            # see if message is setting a context
            if prompt.lower().startswith(env["CONTEXT_PROMPT"]):
                await SqlUtils.enter_message(message.id, "NULL", "system", prompt)
                return
            # if not, set default context
            else:
                if message.reference is None:
                    await SqlUtils.enter_message(message.id, 0, "user", prompt)
                else:
                    await store_locally(message)

    else:
        # print("bot not mentioned")
        # check if local storage is enabled
        if env["STORE_LOCALLY"]:
            await store_locally(message)

    # break if bot sent message
    if message.author == client.user:
        return

    # get thread
    messages = await get_thread(message)

    # if first message is a context message, reply to the thread
    if messages[0]["role"] == "system":
        # get completion
        # response = "test"
        response = await chat_completion(messages)
        # reply to the thread

        # truncate characters over 2000
        MAX_MESSAGE_LENGTH = 2000
        subresponses = [
            response[i : i + MAX_MESSAGE_LENGTH]
            for i in range(0, len(response), MAX_MESSAGE_LENGTH)
        ]
        for subresponse in subresponses:
            print("response", subresponse)
            await message.reply(subresponse)

    return


# run discord client
client.run(env["DISCORD_TOKEN"])
