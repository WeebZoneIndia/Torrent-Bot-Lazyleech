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

import re
import ast
import sys
import html
import inspect
import traceback
import asyncio
from io import BytesIO
from pyrogram import Client, filters
from .. import app, memory_file, ADMIN_CHATS 

@Client.on_message(filters.user(ADMIN_CHATS) & filters.command('sh'))
async def run_shell(client, message):
    command = message.text.split(None, 1)[1]
    if not command:
        await message.reply_text('code 100')
        return
    reply = await message.reply_text('Executing...')
    process = await asyncio.create_subprocess_shell(command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    stdout, stderr = await process.communicate()
    returncode = process.returncode
    text = f'<b>Exit Code:</b> <code>{returncode}</code>\n'
    stdout = stdout.decode().replace('\r', '').strip('\n').rstrip()
    stderr = stderr.decode().replace('\r', '').strip('\n').rstrip()
    if stderr:
        text += f'<code>{html.escape(stderr)}</code>\n'
    if stdout:
        text += f'<code>{html.escape(stdout)}</code>'

    # send as a file if it's longer than 4096 bytes
    if len(text) > 4096:
        out = stderr.strip() + "\n" + stdout.strip()
        f = BytesIO(out.strip().encode('utf-8'))
        f.name = "output.txt"
        await reply.delete()
        await message.reply_document(f, caption=f'<b>Exit Code:</b> <code>{returncode}</code>')
    else:
        await reply.edit_text(text)
