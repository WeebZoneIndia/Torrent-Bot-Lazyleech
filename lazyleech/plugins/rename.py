# lazyleech - Telegram bot primarily to leech from torrents and upload to Telegram
# Copyright (c) 2021 lazyleech developers <theblankx protonmail com, meliodas_bot protonmail com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import os
import time
import html
import asyncio

from pyrogram import Client, filters
from .. import ALL_CHATS

@Client.on_message(filters.command('rename') & filters.chat(ALL_CHATS))
async def rename(client, message):
    data = []
    data.append(message)
    if 'file' in command:
        doc = True
    else:
        doc = False
    name = message.text.split(None, 1)[1]
    if not name:
        await message.reply_text('code 100')
        return
    await message.reply_text('Added to Queue')
    filepath = os.path.join(str(user_id), name)
    await message.reply_text('Downloading...')
    await message.download(file_name=filepath)
    await asyncio.sleep(5)
    await message.reply_text('Uploading...')
    thumb = os.path.join(str(user_id), name)
    if doc is True:
        await message.reply_document(filepath, caption=name)
    else:
        if message.video or (message.document and message.document.mime_type.startswith("video/")):
            duration = message.video.duration if ((message.document is None) and (message.video.thumbs is not None)) else 0
            await message.reply_video(filepath, caption=name, thumb=thumb, duration=duration, width=1280, height=720)
            os.remove(filepath)
    await on_task_complete(data)

async def on_task_complete(data):
    del data[0]
    if len(data) > 0:
        await rename(data[0])
