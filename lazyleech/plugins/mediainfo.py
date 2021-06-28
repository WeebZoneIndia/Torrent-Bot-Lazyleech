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
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from lazyleech.utils.media import post_to_telegraph, runcmd, safe_filename
from .. import ALL_CHATS

@Client.on_message(filters.command('mediainfo') & filters.chat(ALL_CHATS))
async def mediainfo(client, message):
    reply = message.reply_to_message
    if not reply:
        await message.reply_text("Reply to Media first")
        return
    process = await message.reply_text("<b>Processing..</b>")
    x_media = None
    available_media = (
        "audio",
        "document",
        "photo",
        "sticker",
        "animation",
        "video",
        "voice",
        "video_note",
        "new_chat_photo",
    )
    for kind in available_media:
        x_media = getattr(reply, kind, None)
        if x_media is not None:
            break
    if x_media is None:
       await process.edit_text("Reply To a Valid Media Format")
       return
    media_type = str(type(x_media)).split("'")[1]
    file_path = safe_filename(await reply.download())
    output_ = await runcmd(f'mediainfo "{file_path}"')
    out = None
    if len(output_) != 0:
         out = output_[0]
    body_text = f"""
<h2>JSON</h2>
<pre>{x_media}</pre>
<br>
<h2>DETAILS</h2>
<pre>{out or 'Not Supported'}</pre>
"""
    text_ = media_type.split(".")[-1].upper()
    link = post_to_telegraph(media_type, body_text)
    markup = InlineKeyboardMarkup([[InlineKeyboardButton(text=text_, url=link)]])
    await process.edit_text("✨ <b>MEDIA INFO</b>", reply_markup=markup)
