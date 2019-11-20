# -*- coding: future_fstrings -*-

#    Friendly Telegram (telegram userbot)
#    Copyright (C) 2018-2019 The Authors

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.

#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.

import logging

from .. import loader, utils

logger = logging.getLogger(__name__)


def register(cb):
    cb(NotesMod())


class NotesMod(loader.Module):
    """Stores global notes (aka snips)"""
    def __init__(self):
        self.name = _("Notes")

    async def notecmd(self, message):
        """Gets the note specified"""
        args = utils.get_args(message)
        if not args:
            await utils.answer(message, _("What note should be retrieved?"))
            return
        asset_id = self._db.get(__name__, "notes", {}).get(args[0], None)
        logger.debug(asset_id)
        if asset_id is None:
            await utils.answer(message, _("Note not found."))
            return
        await utils.answer(message, await self._db.fetch_asset(asset_id))

    async def savecmd(self, message):
        """Save a new note. Must be used in reply with one parameter (note name)"""
        if not message.is_reply:
            await utils.answer(message, _("You have to reply to a message to save it to a note"))
            return
        args = utils.get_args(message)
        if not args:
            await utils.answer(message, _("You have to provide a name for the note to save"))
            return
        asset_id = await self._db.store_asset(await message.get_reply_message())
        self._db.set(__name__, "notes", {**self._db.get(__name__, "notes", {}), args[0]: asset_id})
        await utils.answer(message, _("Note saved"))

    async def client_ready(self, client, db):
        self._db = db
