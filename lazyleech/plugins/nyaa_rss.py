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

# Source - https://github.com/lostb053/lazyleech/blob/master/lazyleech/plugins/nyaa_auto_download.py

import os
import requests
import re
from bs4 import BeautifulSoup as bs
from motor.motor_asyncio import AsyncIOMotorClient
from motor.core import AgnosticClient, AgnosticDatabase, AgnosticCollection
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from .. import app, ADMIN_CHATS
from pyrogram import Client, filters

rsslink = list(filter(lambda x: x, map(str, os.environ.get("NYAA_RSS_LINKS", "https://nyaa.si/?page=rss&c=0_0&f=0&u=SmallSizedAnimations").split(' '))))

if os.environ.get('DB_URL'):
    DB_URL = os.environ.get('DB_URL')
    _MGCLIENT: AgnosticClient = AsyncIOMotorClient(DB_URL)
    _DATABASE: AgnosticDatabase = _MGCLIENT["SSAFeed"]
    def get_collection(name: str) -> AgnosticCollection:
        """ Create or Get Collection from your database """
        return _DATABASE[name]
    def _close_db() -> None:
        _MGCLIENT.close()
    
    A = get_collection('SSA_TITLE')
    
    async def rss_parser():
        cr = []
        for i in rsslink:
            da = bs(requests.get(i).text, features="html.parser")
            if (await A.find_one({'site':i})) is None:
                await A.insert_one({'_id': str(da.find('item').find('title')), 'site': i})
                return
            count_a = 0
            for ii in da.findAll('item'):
                if (await A.find_one({'site': i}))['_id'] == str(ii.find('title')):
                    break
                cr.append([str(ii.find('title')), (re.sub(r'<.*?>(.*)<.*?>', r'\1', str(ii.find('guid')))).replace('view', 'download')+'.torrent'])
                count_a+=1
            if count_a!=0:
                await A.find_one_and_delete({'site': i})
                await A.insert_one({'_id': str(da.find('item').find('title')), 'site': i})
        for i in cr:
            for ii in ADMIN_CHATS:
                await app.send_message(ii, f"New Anime Released!\n\n{i[0]}\n{i[1]}")

    scheduler = AsyncIOScheduler()
    scheduler.add_job(rss_parser, "interval", minutes=int(os.environ.get('RSS_RECHECK_INTERVAL', 10)), max_instances=5)
    scheduler.start()
