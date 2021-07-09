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

#Credits to https://gitlab.com/blankX

import os
import time
import html
import aiohttp
import asyncio
import datetime
import tempfile
from decimal import Decimal
from datetime import timedelta
from pyrogram import Client, filters
from pyrogram.types import Message
from urllib.parse import quote as urlencode
from .. import ALL_CHATS, help_dict, session
from ..utils.misc import format_bytes, return_progress_string, calculate_eta
from ..utils.upload_worker import upload_queue, upload_statuses, progress_callback_data, upload_waits, stop_uploads

@Client.on_message(filters.command('whatanime') & filters.chat(ALL_CHATS))
async def whatanime(c: Client, m: Message):
    media = m.photo or m.animation or m.video or m.document
    if not media:
        reply = m.reply_to_message
        if not getattr(reply, 'empty', True):
            media = reply.photo or reply.animation or reply.video or reply.document
    if not media:
        await m.reply_text('Photo or GIF or Video required')
        return
    with tempfile.TemporaryDirectory() as tempdir:
        reply = await m.reply_text('Downloading...')
        path = await c.download_media(media, file_name=os.path.join(tempdir, '0'), progress=progress_callback_data, progress_args=(reply,))
        new_path = os.path.join(tempdir, '1.png')
        proc = await asyncio.create_subprocess_exec('ffmpeg', '-i', path, '-frames:v', '1', new_path)
        await proc.communicate()
        await reply.edit_text('Uploading...')
        with open(new_path, 'rb') as file:
            async with session.post('https://api.trace.moe/search?cutBorders&anilistInfo', data={'image': file}) as resp:
                json = await resp.json()
    if json.get('error'):
        await reply.edit_text(json['error'], parse_mode=None)
    else:
        try:
            match = json['result'][0]
        except IndexError:
            await reply.edit_text('No match')
        else:
            nsfw = match['anilist']['isAdult']
            title_native = match['anilist']['title']['native']
            title_english = match['anilist']['title']['english']
            title_romaji = match['anilist']['title']['romaji']
            synonyms = ', '.join(match['anilist']['synonyms'])
            anilist_id = match['anilist']['id']
            episode = match['episode']
            similarity = match['similarity']
            from_time = str(datetime.timedelta(seconds=match['from'])).split('.', 1)[0].rjust(8, '0')
            to_time = str(datetime.timedelta(seconds=match['to'])).split('.', 1)[0].rjust(8, '0')
            text = f'<a href="https://anilist.co/anime/{anilist_id}">{title_romaji}</a>'
            if title_english:
                text += f' ({title_english})'
            if title_native:
                text += f' ({title_native})'
            if synonyms:
                text += f'\n<b>Synonyms:</b> {synonyms}'
            text += f'\n<b>Similarity:</b> {(Decimal(similarity) * 100).quantize(Decimal(".01"))}%\n'
            if episode:
                text += f'<b>Episode:</b> {episode}\n'
            if nsfw:
                text += '<b>Hentai/NSFW:</b> Yes'

            async def _send_preview():
                with tempfile.NamedTemporaryFile() as file:
                    async with session.get(match['video']) as resp:
                        while True:
                            chunk = await resp.content.read(4096)
                            if not chunk:
                                break
                            file.write(chunk)
                    file.seek(0)
                    try:
                        await reply.reply_video(file.name, caption=f'{from_time} - {to_time}')
                    except BaseException:
                        await reply.reply_text('Cannot send preview :/')
            await asyncio.gather(reply.edit_text(text, disable_web_page_preview=True), _send_preview())

            
help_dict['extras'] = ('Extras',
'''<b>Miscs</b>
/mediainfo <i>[replied media]</i> 
/whatanime <i>[replied media]</i>

<b>Youtube-DL</b>
/ytdl <i>Youtube Link</i>
/youtube <i>Youtube Link</i>''')
