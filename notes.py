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


@loader.tds
class NotesMod(loader.Module):
    """Stores global notes (aka snips)"""
    strings = {"name": "Notes",
               "what_note": "<b>What note should be retrieved?</b>",
               "no_note": "<b>Note not found</b>",
               "save_what": "<b>You must reply to a message to save it to a note, or type the note.</b>",
               "what_name": "<b>You must specify what the note should be called?",
               "saved": "<b>Note saved</b>",
               "notes_header": "<b>Saved notes:</b>\n\n",
               "notes_item": "<b>•</b> <code>{}</code>",
               "delnote_args": "<b>What note should be deleted?</b>",
               "delnote_done": "<b>Note deleted</b>",
               "delnotes_none": "<b>There are no notes to be cleared</b>",
               "delnotes_done": "<b>All notes cleared</b>",
               "notes_none": "<b>There are no saved notes</b>"}

    def config_complete(self):
        self.name = self.strings["name"]

    async def notecmd(self, message):
        """Gets the note specified"""
        args = utils.get_args(message)
        if not args:
            await utils.answer(message, self.strings["what_note"])
            return
        asset_id = self._db.get(__name__, "notes", {}).get(args[0], None)
        logger.debug(asset_id)
        if asset_id is None:
            await utils.answer(message, self.strings["no_note"])
            return
        await utils.answer(message, await self._db.fetch_asset(asset_id))

    async def delallnotescmd(self, message):
        """Deletes all the saved notes"""
        if not self._db.get(__name__, "notes", {}):
            await utils.answer(message, self.strings["delnotes_none"])
            return
        self._db.get(__name__, "notes", {}).clear()
        await utils.answer(message, self.strings["delnotes_done"])

    async def savecmd(self, message):
        """Save a new note. Must be used in reply with one parameter (note name)"""
        args = utils.get_args(message)
        if not args:
            await utils.answer(message, self.strings["what_name"])
            return
        if not message.is_reply:
            if len(args) < 2:
                await utils.answer(message, self.strings["save_what"])
                return
            else:
                message.entities = None
                message.message = args[1]
                target = message
                logger.debug(target.message)
        else:
            target = await message.get_reply_message()
        asset_id = await self._db.store_asset(target)
        self._db.set(__name__, "notes", {**self._db.get(__name__, "notes", {}), args[0]: asset_id})
        await utils.answer(message, self.strings["saved"])

    async def delnotecmd(self, message):
        """Deletes a note, specified by note name"""
        args = utils.get_args(message)
        if not args:
            await utils.answer(message, self.strings["delnote_args"])
        old = self._db.get(__name__, "notes", {})
        del old[args[0]]
        self._db.set(__name__, "notes", old)
        await utils.answer(message, self.strings["delnote_done"])

    async def notescmd(self, message):
        """List the saved notes"""
        if not self._db.get(__name__, "notes", {}):
            await utils.answer(message, self.strings["notes_none"])
            return
        await utils.answer(message, self.strings["notes_header"]
                           + "\n".join(self.strings["notes_item"].format(key)
                           for key in self._db.get(__name__, "notes", {})))

    async def watcher(self, message):
        args = message.text
        notes = self._db.get(__name__, "notes", {})
        if args.startswith("#"):
            for key in notes:
                if args[1:] in notes:
                    value = await self._db.fetch_asset(notes[key])
            await utils.answer(message, value)

    async def client_ready(self, client, db):
        self._db = db
