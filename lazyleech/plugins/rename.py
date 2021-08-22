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

@Client.on_message(filters.command(['rename', 'renamefile']) & filters.chat(ALL_CHATS))
async def rename(client, message):
    name = message.text.split(None, 1)[1]
    msg = await message.reply_text('Added to Queue')
    data = []
    data.append(message)
    filepath = os.path.join(str(message.from_user.id), name)
    await msg.edit_text('<code>Downloading...</code>')
    await message.reply.download(file_name=filepath)
    await asyncio.sleep(5)
    await msg.edit_text('<code>Uploading...</code>')
    await message.reply_document(filepath, caption=name)
    await msg.delete()
    os.remove(filepath)
    await on_task_complete(data)

async def on_task_complete(data):
    del data[0]
    if len(data) > 0:
        await rename(data[0])
