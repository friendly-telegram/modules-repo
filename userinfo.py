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

from .. import loader, utils
import logging

from telethon.tl.functions.users import GetFullUserRequest

logger = logging.getLogger(__name__)


def register(cb):
    cb(UserInfoMod())


class UserInfoMod(loader.Module):
    """Tells you about people"""
    def __init__(self):
        self.name = _("User Info")

    async def userinfocmd(self, message):
        """Use in reply to get user info"""
        if message.is_reply:
            full = await self.client(GetFullUserRequest((await message.get_reply_message()).from_id))
        else:
            args = utils.get_args(message)
            if not args:
                return await utils.answer(message, '<b>No args or reply was provided.</b>')
            try:
                full = await self.client(GetFullUserRequest(args[0]))
            except ValueError:
                return await utils.answer(message, _("<b>Couldn't find that user.</b>"))
        logger.debug(full)
        reply = _("First name: <code>{}</code>").format(utils.escape_html(ascii(full.user.first_name)))
        if full.user.last_name is not None:
            reply += _("\nLast name: <code>{}</code>").format(utils.escape_html(ascii(full.user.last_name)))
        reply += _("\nBio: <code>{}</code>").format(utils.escape_html(ascii(full.about)))
        reply += _("\nRestricted: <code>{}</code>").format(utils.escape_html(str(full.user.restricted)))
        reply += _("\nDeleted: <code>{}</code>").format(utils.escape_html(str(full.user.deleted)))
        reply += _("\nBot: <code>{}</code>").format(utils.escape_html(str(full.user.bot)))
        reply += _("\nVerified: <code>{}</code>").format(utils.escape_html(str(full.user.verified)))
        if full.user.photo:
            reply += _("\nDC ID: <code>{}</code>").format(utils.escape_html(str(full.user.photo.dc_id)))
        await message.edit(reply)

    async def permalinkcmd(self, message):
        """Get permalink to user based on ID or username"""
        args = utils.get_args(message)
        if len(args) < 1:
            await message.edit(_("Provide a user to locate"))
            return
        try:
            user = int(args[0])
        except ValueError:
            user = args[0]
        try:
            user = await self.client.get_input_entity(user)
        except ValueError as e:
            logger.debug(e)
            # look for the user
            await message.edit(_("Searching for user..."))
            await self.client.get_dialogs()
            try:
                user = await self.client.get_input_entity(user)
            except ValueError:
                await message.edit(_("Can't find user."))
                return
        if len(args) > 1:
            await utils.answer(message, "<a href='tg://user?id={uid}'>{txt}</a>".format(uid=user.user_id, txt=args[1]))
        else:
            await message.edit(_("<a href='tg://user?id={uid}'>Permalink to {uid}</a>").format(uid=user.user_id))

    async def client_ready(self, client, db):
        self.client = client
