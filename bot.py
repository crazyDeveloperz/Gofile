import pyrogram
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import requests
import time
import os
import math

# अपनी API ID, API Hash और Bot Token यहाँ डालें
API_ID = 25069425
API_HASH = "41034e257e6449615faea5f18bbe1dd7"
BOT_TOKEN = "7500475870:AAH3w0cVAWBjZvceWmpM70Ul573t-5v-74I"

app = Client(
    "GofileBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

def upload_to_gofile(file_path):
    try:
        # GoFile सर्वर प्राप्त करें
        getServer = requests.get("https://api.gofile.io/getServer")
        getServer.raise_for_status()  # त्रुटियों की जाँच करें
        server = getServer.json()["data"]["server"]

        # फ़ाइल अपलोड करें
        url = f"https://{server}.gofile.io/uploadFile"
        with open(file_path, "rb") as f:
            uploadFile = requests.post(url, files={"file": f})
            uploadFile.raise_for_status()
            file_id = uploadFile.json()["data"]["fileId"]
            download_page = f"https://gofile.io/d/{file_id}"
            return download_page
    except requests.exceptions.RequestException as e:
        print(f"GoFile पर अपलोड करने में त्रुटि: {e}")
        return None
    except (KeyError, TypeError) as e:
        print(f"GoFile API प्रतिक्रिया में त्रुटि: {e}")
        return None

@app.on_message(filters.document | filters.video)
async def handle_file(client, message):
    try:
        # डाउनलोड प्रोग्रेस दिखाने के लिए एक संदेश भेजें
        download_message = await message.reply_text("डाउनलोड शुरू...")

        # फ़ाइल डाउनलोड करें और प्रोग्रेस दिखाएँ
        start_time = time.time()
        file_path = await client.download_media(
            message,
            progress=lambda current, total: download_progress(current, total, message, download_message, start_time)
        )

        await download_message.edit_text("अपलोड शुरू...")

        # GoFile पर अपलोड करें
        gofile_link = upload_to_gofile(file_path)

        if gofile_link:
            await download_message.edit_text(f"फ़ाइल अपलोड हो गई! यहाँ डाउनलोड लिंक है:\n{gofile_link}")
        else:
            await download_message.edit_text("फ़ाइल अपलोड करने में त्रुटि आई।")

        os.remove(file_path) # स्थानीय फ़ाइल हटाएँ

    except Exception as e:
        print(f"फ़ाइल हैंडलिंग में त्रुटि: {e}")
        await message.reply_text("फ़ाइल प्रोसेस करने में त्रुटि आई।")

def download_progress(current, total, message, download_message, start):
    """डाउनलोड प्रोग्रेस बार दिखाएँ"""
    now = time.time()
    diff = now - start
    if diff < 1:
        return
    else:
        percentage = current * 100 / total
        speed = current / diff
        elapsed_time = round(diff)
        time_to_completion = round((total - current) / speed)
        estimated_total_time = elapsed_time + time_to_completion

        elapsed_time = TimeFormatter(elapsed_time)
        estimated_total_time = TimeFormatter(estimated_total_time)

        progress = "[{0}{1}] {2}%".format(
            "".join(["●" for i in range(math.floor(percentage / 10))]),
            "".join(["○" for i in range(10 - math.floor(percentage / 10))]),
            round(percentage, 2),
        )

        tmp = f"""
**डाउनलोडिंग:**
{progress}
**स्पीड:** {humanbytes(speed)}/s
**बीता हुआ समय:** {elapsed_time}
**अनुमानित कुल समय:** {estimated_total_time}
        """
        try:
            download_message.edit(tmp)
        except:
            pass

def humanbytes(size):
    """फ़ाइल साइज़ को मानव-पठनीय फ़ॉर्मेट में बदलें"""
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
    """समय को HH:MM:SS फ़ॉर्मेट में बदलें"""
    minutes, seconds = divmod(int(milliseconds), 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    tmp = ((str(days) + "d, ") if days else "") + \
        ((str(hours) + "h, ") if hours else "") + \
        ((str(minutes) + "m, ") if minutes else "") + \
        ((str(seconds) + "s, ") if seconds else "")
    return tmp[:-2]

print("Bot started!")
app.run()
  
