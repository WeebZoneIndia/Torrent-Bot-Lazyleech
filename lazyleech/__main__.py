import asyncio
import logging
import traceback
from pyrogram import idle
from . import app, ADMIN_CHATS, preserved_logs
from .utils.upload_worker import upload_worker

logging.basicConfig(level=logging.INFO)
logging.getLogger('pyrogram.syncer').setLevel(logging.WARNING)

async def main():
    async def _autorestart_worker():
        while True:
            try:
                await upload_worker()
            except Exception as ex:
                preserved_logs.append(ex)
                logging.exception('upload worker commited suicide')
                tb = traceback.format_exc()
                for i in ADMIN_CHATS:
                    try:
                        await app.send_message(i, 'upload worker commited suicide')
                        await app.send_message(i, tb, parse_mode=None)
                    except Exception:
                        logging.exception('failed %s', i)
                        tb = traceback.format_exc()
    asyncio.create_task(_autorestart_worker())
    await app.start()
    await idle()
    await app.stop()

app.loop.run_until_complete(main())
