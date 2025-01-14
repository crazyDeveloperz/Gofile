import pyrogram
from pyrogram import Client, filters
import requests
import time
import os
import math

# Your API credentials
API_ID = 25069425
API_HASH = "41034e257e6449615faea5f18bbe1dd7"
BOT_TOKEN = "7500475870:AAH3w0cVAWBjZvceWmpM70Ul573t-5v-74I"

app = Client("GofileBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

def upload_to_gofile(file_path):
    """Uploads a file to GoFile and returns the download link."""
    try:
        get_server_url = "https://api.gofile.io/getServer"
        response = requests.get(get_server_url)
        response.raise_for_status()
        server_info = response.json()["data"]["server"]

        upload_url = f"https://{server_info}.gofile.io/uploadFile"

        with open(file_path, "rb") as f:
            upload_response = requests.post(upload_url, files={"file": f})
            upload_response.raise_for_status()

        file_id = upload_response.json()["data"]["fileId"]
        return f"https://gofile.io/d/{file_id}"

    except requests.exceptions.RequestException as e:
        print(f"Error uploading to GoFile: {e}")
        return None
    except (KeyError, TypeError) as e:
        print(f"GoFile API response error: {e}")
        return None

def humanbytes(size):
    """Convert file size to human-readable format."""
    if not size:
        return ""
    power = 2**10
    n = 0
    power_labels = {0 : '', 1: 'KB', 2: 'MB', 3: 'GB', 4: 'TB'}
    while size > power:
        size /= power
        n += 1
    return f"{size:.2f} {power_labels[n]}"

def TimeFormatter(milliseconds: int) -> str:
    """Convert time to HH:MM:SS format."""
    minutes, seconds = divmod(int(milliseconds), 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    tmp = ((str(days) + "d, ") if days else "") + \
        ((str(hours) + "h, ") if hours else "") + \
        ((str(minutes) + "m, ") if minutes else "") + \
        ((str(seconds) + "s, ") if seconds else "")
    return tmp[:-2]

async def download_progress(current, total, message, download_message, start):
    """Display download progress."""
    now = time.time()
    diff = now - start
    if diff < 1:
        return
    percentage = current * 100 / total
    speed = current / diff
    elapsed_time = round(diff)
    time_to_completion = round((total - current) / speed) if speed > 0 else 0 # Avoid division by zero
    estimated_total_time = elapsed_time + time_to_completion

    elapsed_time = TimeFormatter(elapsed_time)
    estimated_total_time = TimeFormatter(estimated_total_time)

    progress = "[{0}{1}] {2}%".format(
        "".join(["●" for i in range(math.floor(percentage / 10))]),
        "".join(["○" for i in range(10 - math.floor(percentage / 10))]),
        round(percentage, 2),
    )

    tmp = f"""
**Downloading:**
{progress}
**Speed:** {humanbytes(speed)}/s
**Elapsed Time:** {elapsed_time}
**Estimated Total Time:** {estimated_total_time}
    """
    try:
        await download_message.edit(tmp)
    except:
        pass


@app.on_message(filters.document | filters.video)
async def handle_file(client, message):
    try:
        download_message = await message.reply_text("Downloading...")
        start_time = time.time()
        file_path = await client.download_media(
            message,
            progress=lambda current, total: download_progress(current, total, message, download_message, start_time)
        )

        await download_message.edit_text("Uploading...")
        gofile_link = upload_to_gofile(file_path)

        if gofile_link:
            await download_message.edit_text(f"File uploaded! Download link:\n{gofile_link}")
        else:
            await download_message.edit_text("Error uploading file.")

        os.remove(file_path)

    except Exception as e:
        print(f"Error handling file: {e}")
        await message.reply_text("Error processing file.")

print("Bot started!")
app.run()
