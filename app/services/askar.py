from flask import current_app
from aries_askar import Store
import hashlib
import json
import logging
from config import Config

logger = logging.getLogger(__name__)

class AskarStorage:
    def __init__(self):
        self.db = Config.ASKAR_DB

    async def provision(self, recreate=False):
        logger.info(self.db)
        await Store.provision(self.db, "none", recreate=recreate)
        
    async def get_wallet_info(self, client_id):
        return await self.fetch(category='wallet', data_key=client_id)

    async def open(self):
        return await Store.open(self.db, "none")

    async def fetch(self, category, data_key):
        store = await self.open()
        try:
            async with store.session() as session:
                entry = await session.fetch(category, data_key)
            return json.loads(entry.value)
        except:
            return None

    async def fetch_name_by_tag(self, category, tags):
        store = await self.open()
        try:
            current_app.logger.warning('Fetching Name')
            current_app.logger.warning(category)
            # current_app.logger.warning(tags)
            async with store.session() as session:
                entries = await session.fetch_all(category, tags)
            current_app.logger.warning(entries.handle.get_name(0))
            return entries.handle.get_name(0)
        except:
            return None

    async def fetch_entry_by_tag(self, category, tags):
        store = await self.open()
        try:
            async with store.session() as session:
                entries = await session.fetch_all(category, tags)
                current_app.logger.warning(entries)
                entries = entries.handle.get_value(0)
            return json.loads(entries)
        except:
            return None

    async def append(self, category, data_key, data, tags=None):
        store = await self.open()
        try:
            current_app.logger.warning('Appending Data')
            current_app.logger.warning(category)
            current_app.logger.warning(data_key)
            async with store.session() as session:
                entries = await session.fetch(category, data_key)
                entries = json.loads(entries.value)
                entries.append(data)
                await session.replace(
                    category,
                    data_key,
                    json.dumps(entries),
                    tags,
                )
        except:
            return False

    async def store(self, category, data_key, data, tags=None):
        store = await self.open()
        try:
            async with store.session() as session:
                await session.insert(
                    category,
                    data_key,
                    json.dumps(data),
                    tags,
                )
        except:
            return False

    async def update(self, category, data_key, data, tags=None):
        store = await self.open()
        try:
            async with store.session() as session:
                await session.replace(
                    category,
                    data_key,
                    json.dumps(data),
                    tags,
                )
        except:
            return False