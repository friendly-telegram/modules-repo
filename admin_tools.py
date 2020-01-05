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

from telethon.tl.types import ChatAdminRights, ChatBannedRights, PeerUser, PeerChannel
from telethon.errors import BadRequestError
from telethon.tl.functions.channels import EditAdminRequest, EditBannedRequest

logger = logging.getLogger(__name__)


def register(cb):
    cb(BanMod())


@loader.tds
class BanMod(loader.Module):
    """Group administration tasks"""
    strings = {"name": "Administration",
               "ban_not_supergroup": "<b>I can't ban someone unless they're in a supergroup!</b>",
               "unban_not_supergroup": "<b>I can't unban someone unless they're banned from a supergroup!</b>",
               "kick_not_group": "<b>I can't kick someone unless they're in a group!</b>",
               "ban_none": "<b>I can't ban no-one, can I?</b>",
               "unban_none": "<b>I need someone to unbanned here.</b>",
               "kick_none": "<b>I need someone to be kicked out of the chat.</b>",
               "promote_none": "<b>I can't promote no one, can I?</b>",
               "demote_none": "<b>I can't demote no one, can I?</b>",
               "who": "<b>Who the hell is that?</b>",
               "not_admin": "<b>Am I an admin here?</b>",
               "banned": "<b>Banned</b> <code>{}</code> <b>from the chat!</b>",
               "unbanned": "<b>Unbanned</b> <code>{}</code> <b>from the chat!</b>",
               "kicked": "<b>Kicked</b> <code>{}</code> <b>from the chat!</b>",
               "promoted": "<code>{}</code> <b>is now powered with admin rights!</b>",
               "demoted": "<code>{}</code> <b>is now stripped off of their admin rights!</b>"}

    def __init__(self):
        self.name = self.strings["name"]

    async def bancmd(self, message):
        """Ban the user from the group"""
        if not isinstance(message.to_id, PeerChannel):
            return await utils.answer(message, self.strings["not_supergroup"])
        if message.is_reply:
            user = await utils.get_user(await message.get_reply_message())
        else:
            args = utils.get_args(message)
            if len(args) == 0:
                return await utils.answer(message, self.strings["ban_none"])
            user = await self.client.get_entity(args[0])
        if not user:
            return await utils.answer(message, self.strings["who"])
        logger.debug(user)
        try:
            await self.client(EditBannedRequest(message.chat_id, user.id,
                                                ChatBannedRights(until_date=None, view_messages=True)))
        except BadRequestError:
            await utils.answer(message, self.strings["not_admin"])
        else:
            await self.allmodules.log("ban", group=message.chat_id, affected_uids=[user.id])
            await utils.answer(message, self.strings["banned"].format(utils.escape_html(ascii(user.first_name))))

    async def unbancmd(self, message):
        """Lift the ban off the user."""
        if not isinstance(message.to_id, PeerChannel):
            return await utils.answer(message, self.strings["unban_not_supergroup"])
        if message.is_reply:
            user = await utils.get_user(await message.get_reply_message())
        else:
            args = utils.get_args(message)
            if len(args) == 0:
                return await utils.answer(message, self.strings["unban_none"])
            user = await self.client.get_entity(args[0])
        if not user:
            return await utils.answer(message, self.strings["who"])
        logger.debug(user)
        try:
            await self.client(EditBannedRequest(message.chat_id, user.id,
                              ChatBannedRights(until_date=None, view_messages=False)))
        except BadRequestError:
            await utils.answer(message, self.strings["not_admin"])
        else:
            await self.allmodules.log("unban", group=message.chat_id, affected_uids=[user.id])
            await utils.answer(message, self.strings["unbanned"].format(utils.escape_html(ascii(user.first_name))))

    async def kickcmd(self, message):
        """Kick the user out of the group"""
        if isinstance(message.to_id, PeerUser):
            return await utils.answer(message, self.strings["kick_not_group"])
        if message.is_reply:
            user = await utils.get_user(await message.get_reply_message())
        else:
            args = utils.get_args(message)
            if len(args) == 0:
                return await utils.answer(message, self.strings["kick_none"])
            user = await self.client.get_entity(args[0])
        if not user:
            return await utils.answer(message, self.strings["who"])
        logger.debug(user)
        try:
            await self.client.kick_participant(message.chat_id, user.id)
        except BadRequestError:
            await utils.answer(message, self.strings["not_admin"])
        else:
            await self.allmodules.log("kick", group=message.chat_id, affected_uids=[user.id])
            await utils.answer(message, self.strings["kicked"].format(utils.escape_html(ascii(user.first_name))))

    async def promotecmd(self, message):
        """Provides admin rights to the specified user."""
        if message.is_reply:
            user = await utils.get_user(await message.get_reply_message())
        else:
            args = utils.get_args(message)
            if len(args) == 0:
                return await utils.answer(message, self.strings["promote_none"])
            user = await self.client.get_entity(args[0])
        if not user:
            return await utils.answer(message, self.strings["who"])
        logger.debug(user)
        try:
            await self.client(EditAdminRequest(message.chat_id, user.id,
                              ChatAdminRights(post_messages=None,
                                              add_admins=None,
                                              invite_users=None,
                                              change_info=None,
                                              ban_users=None,
                                              delete_messages=True,
                                              pin_messages=True,
                                              edit_messages=None), "Admin"))
        except BadRequestError:
            await utils.answer(message, self.strings["not_admin"])
        else:
            await self.allmodules.log("promote", group=message.chat_id, affected_uids=[user.id])
            await utils.answer(message, self.strings["promoted"].format(utils.escape_html(ascii(user.first_name))))

    async def demotecmd(self, message):
        """Removes admin rights of the specified group admin."""
        if message.is_reply:
            user = await utils.get_user(await message.get_reply_message())
        else:
            args = utils.get_args(message)
            if len(args) == 0:
                return await utils.answer(message, self.strings["demote_none"])
            user = await self.client.get_entity(args[0])
        if not user:
            return await utils.answer(message, self.strings["who"])
        logger.debug(user)
        try:
            await self.client(EditAdminRequest(message.chat_id, user.id,
                              ChatAdminRights(post_messages=None,
                                              add_admins=None,
                                              invite_users=None,
                                              change_info=None,
                                              ban_users=None,
                                              delete_messages=None,
                                              pin_messages=None,
                                              edit_messages=None), "Admin"))
        except BadRequestError:
            await utils.answer(message, self.strings["not_admin"])
        else:
            await self.allmodules.log("demote", group=message.chat_id, affected_uids=[user.id])
            await utils.answer(message, self.strings["demoted"].format(utils.escape_html(ascii(user.first_name))))

    async def client_ready(self, client, db):
        self.client = client
