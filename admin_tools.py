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

from telethon.tl.types import ChatBannedRights, PeerUser, PeerChannel
from telethon.errors import BadRequestError
from telethon.tl.functions.channels import EditBannedRequest

logger = logging.getLogger(__name__)


def register(cb):
    cb(BanMod())


class BanMod(loader.Module):
    """Group administration tasks"""
    def __init__(self):
        self.name = _("Administration")

    async def bancmd(self, message):
        """Ban the user from the group"""
        if not isinstance(message.to_id, PeerChannel):
            return await utils.answer(message,
                                      _("You can't ban someone unless they're in a supergroup! Try blocking them."))
        if message.is_reply:
            user = await utils.get_user(await message.get_reply_message())
        else:
            args = utils.get_args(message)
            if len(args) == 0:
                return await utils.answer(message, _("I can't ban no-one, can I?"))
            user = await self.client.get_entity(args[0])
        if not user:
            return await message.edit(_("Who the hell is that?"))
        logger.debug(user)
        try:
            await self.client(EditBannedRequest(message.chat_id, user.id,
                                                ChatBannedRights(until_date=None, view_messages=True)))
        except BadRequestError:
            await message.edit(_("Am I an admin here?"))
        else:
            await self.allmodules.log("ban", group=message.chat_id, affected_uids=[user.id])
            await utils.answer(message, _("Banned <code>{}</code> from the chat!")
                               .format(utils.escape_html(ascii(user.first_name))))

    async def unbancmd(self, message):
        """Lift the ban off the user."""
        if not isinstance(message.to_id, PeerChannel):
            return await utils.answer(message, _("You can't unban someone unless they're banned from a supergroup!"))
        if message.is_reply:
            user = await utils.get_user(await message.get_reply_message())
        else:
            args = utils.get_args(message)
            if len(args) == 0:
                return await utils.answer(message, _("Who should be unbanned?"))
            user = await self.client.get_entity(args[0])
        if not user:
            return await message.edit(_("I couldn't find who to unban."))
        logger.debug(user)
        try:
            await self.client(EditBannedRequest(message.chat_id, user.id,
                              ChatBannedRights(until_date=None, view_messages=False)))
        except BadRequestError:
            await message.edit(_("Am I an admin here?"))
        else:
            await self.allmodules.log("unban", group=message.chat_id, affected_uids=[user.id])
            await utils.answer(message, _("Unbanned <code>{}</code> from the chat!")
                               .format(utils.escape_html(ascii(user.first_name))))

    async def kickcmd(self, message):
        """Kick the user out of the group"""
        if isinstance(message.to_id, PeerUser):
            return await utils.answer(message,
                                      _("You can't kick someone unless they're in a group! Try blocking them."))
        if message.is_reply:
            user = await utils.get_user(await message.get_reply_message())
        else:
            args = utils.get_args(message)
            if len(args) == 0:
                return await utils.answer(message, _("Who should be kicked?"))
            user = await self.client.get_entity(args[0])
        if not user:
            return await message.edit(_("I couldn't find who to kick."))
        logger.debug(user)
        try:
            await self.client.kick_participant(message.chat_id, user.id)
        except BadRequestError:
            await message.edit(_("Am I an admin here?"))
        else:
            await self.allmodules.log("kick", group=message.chat_id, affected_uids=[user.id])
            await message.edit(_("Kicked <code>{}</code> from the chat!")
                               .format(utils.escape_html(ascii(user.first_name))))

    async def client_ready(self, client, db):
        self.client = client
