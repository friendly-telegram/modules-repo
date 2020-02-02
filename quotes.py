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
import requests
import base64
import json
import telethon

from .. import loader, utils
from PIL import Image
from io import BytesIO

logger = logging.getLogger(__name__)


def register(cb):
    cb(QuotesMod())


@loader.tds
class QuotesMod(loader.Module):
    """Quote a message."""
    strings = {
        "name": "Quotes",
        "api_token_cfg_doc": "API Key/Token for Quotes.",
        "api_url_cfg_doc": "API URL for Quotes.",
        "colors_cfg_doc": "Username colors",
        "default_username_color_cfg_doc": "Default color for the username.",
        "no_reply": "<b>You didn't reply to a message.</b>",
        "no_template": "<b>You didn't specify the template.</b>",
        "delimiter": "</code>, <code>",
        "server_error": "<b>Server error. Please report to developer.</b>",
        "invalid_token": "<b>You've set an invalid token.</b>",
        "unauthorized": "<b>You're unauthorized to do this.</b>",
        "not_enough_permissions": "<b>Wrong template. You can use only the default one.</b>",
        "templates": "<b>Available Templates:</b> <code>{}</code>",
        "cannot_send_stickers": "<b>You cannot send stickers in this chat.</b>",
        "admin": "admin",
        "creator": "creator",
        "hidden": "hidden",
        "channel": "Channel",
        "filename": "file.png"
    }

    def __init__(self):
        self.config = loader.ModuleConfig("api_token", None, lambda: self.strings["api_token_cfg_doc"],
                                          "api_url", "http://api.antiddos.systems",
                                          lambda: self.strings["api_url_cfg_doc"],
                                          "username_colors", ["#fb6169", "#faa357", "#b48bf2", "#85de85",
                                                              "#62d4e3", "#65bdf3", "#ff5694"],
                                          lambda: self.strings["colors_cfg_doc"],
                                          "default_username_color", "#b48bf2",
                                          lambda: self.strings["default_username_color_cfg_doc"])

    def config_complete(self):
        self.name = self.strings["name"]

    async def client_ready(self, client, db):
        self.client = client

    async def quotecmd(self, message):  # noqa: C901
        """Quote a message.
        Usage: .quote [template] [file/force_file]
        If template is missing, possible templates are fetched.
        If no args provided, default template will be used, quote sent as sticker"""
        args = utils.get_args(message)
        reply = await message.get_reply_message()

        if not reply:
            return await utils.answer(message, self.strings["no_reply"])

        username_color = username = admintitle = user_id = None
        profile_photo_url = reply.from_id

        admintitle = ""
        pfp = None
        if isinstance(reply.to_id, telethon.tl.types.PeerChannel) and reply.fwd_from:
            user = reply.forward.chat
        elif isinstance(reply.to_id, telethon.tl.types.PeerChat):
            chat = await self.client(telethon.tl.functions.messages.GetFullChatRequest(reply.to_id))
            participants = chat.full_chat.participants.participants
            participant = next(filter(lambda x: x.user_id == reply.from_id, participants), None)
            if isinstance(participant, telethon.tl.types.ChatParticipantCreator):
                admintitle = self.strings["creator"]
            elif isinstance(participant, telethon.tl.types.ChatParticipantAdmin):
                admintitle = self.strings["admin"]
            user = await reply.get_sender()
        else:
            user = await reply.get_sender()

        username = telethon.utils.get_display_name(user)
        if reply.fwd_from is not None and reply.fwd_from.post_author is not None:
            username += f" ({reply.fwd_from.post_author})"
        user_id = reply.from_id

        if reply.fwd_from:
            if reply.fwd_from.saved_from_peer:
                profile_photo_url = reply.forward.chat
                admintitle = self.strings["channel"]
            elif reply.fwd_from.from_name:
                username = reply.fwd_from.from_name
                profile_photo_url = None
                admintitle = ""
            elif reply.forward.sender:
                username = telethon.utils.get_display_name(reply.forward.sender)
                profile_photo_url = reply.forward.sender.id
                admintitle = ""
            elif reply.forward.chat:
                admintitle = self.strings["channel"]
                profile_photo_url = user
        else:
            if isinstance(reply.to_id, telethon.tl.types.PeerUser) is False:
                try:
                    user = await self.client(telethon.tl.functions.channels.GetParticipantRequest(message.chat_id,
                                                                                                  user))
                    if isinstance(user.participant, telethon.tl.types.ChannelParticipantCreator):
                        admintitle = user.participant.rank or self.strings["creator"]
                    elif isinstance(user.participant, telethon.tl.types.ChannelParticipantAdmin):
                        admintitle = user.participant.rank or self.strings["admin"]
                    user = user.users[0]
                except telethon.errors.rpcerrorlist.UserNotParticipantError:
                    pass
        if profile_photo_url is not None:
            pfp = await self.client.download_profile_photo(profile_photo_url, bytes)

        if pfp is not None:
            profile_photo_url = "data:image/png;base64, " + base64.b64encode(pfp).decode()
        else:
            profile_photo_url = ""

        if user_id is not None:
            username_color = self.config["username_colors"][user_id % 7]
        else:
            username_color = self.config["default_username_color"]

        reply_username = ""
        reply_text = ""
        if reply.is_reply is True:
            reply_to = await reply.get_reply_message()
            reply_peer = None
            if reply_to.fwd_from is not None:
                if reply_to.forward.chat is not None:
                    reply_peer = reply_to.forward.chat
                elif reply_to.fwd_from.from_id is not None:
                    try:
                        user_id = reply_to.fwd_from.from_id
                        user = await self.client(telethon.tl.functions.users.GetFullUserRequest(user_id))
                        reply_peer = user.user
                    except ValueError:
                        pass
                else:
                    reply_username = reply_to.fwd_from.from_name
            elif reply_to.from_id is not None:
                reply_user = await self.client(telethon.tl.functions.users.GetFullUserRequest(reply_to.from_id))
                reply_peer = reply_user.user

            if reply_username is None or reply_username == "":
                reply_username = telethon.utils.get_display_name(reply_peer)
            reply_text = reply_to.message

        date = ""
        if reply.fwd_from is not None:
            date = reply.fwd_from.date.strftime("%H:%M")
        else:
            date = reply.date.strftime("%H:%M")

        request = json.dumps({
            "ProfilePhotoURL": profile_photo_url,
            "usernameColor": username_color,
            "username": username,
            "adminTitle": admintitle,
            "Text": reply.message,
            "Markdown": get_markdown(reply),
            "ReplyUsername": reply_username,
            "ReplyText": reply_text,
            "Date": date,
            "Template": args[0] if len(args) > 0 else "default",
            "APIKey": self.config["api_token"]
        })

        resp = await utils.run_sync(requests.post, self.config["api_url"] + "/api/v2/quote", data=request)
        resp.raise_for_status()
        resp = await utils.run_sync(resp.json)

        if resp["status"] == 500:
            return await utils.answer(message, self.strings["server_error"])
        elif resp["status"] == 401:
            if resp["message"] == "ERROR_TOKEN_INVALID":
                return await utils.answer(message, self.strings["invalid_token"])
            else:
                raise ValueError("Invalid response from server", resp)
        elif resp["status"] == 403:
            if resp["message"] == "ERROR_UNAUTHORIZED":
                return await utils.answer(message, self.strings["unauthorized"])
            else:
                raise ValueError("Invalid response from server", resp)
        elif resp["status"] == 404:
            if resp["message"] == "ERROR_TEMPLATE_NOT_FOUND":
                newreq = await utils.run_sync(requests.post, self.config["api_url"] + "/api/v1/getalltemplates", data={
                    "token": self.config["api_token"]
                })
                newreq = await utils.run_sync(newreq.json)

                if newreq["status"] == "NOT_ENOUGH_PERMISSIONS":
                    return await utils.answer(message, self.strings["not_enough_permissions"])
                elif newreq["status"] == "SUCCESS":
                    templates = self.strings["delimiter"].join(newreq["message"])
                    return await utils.answer(message, self.strings["templates"].format(templates))
                elif newreq["status"] == "INVALID_TOKEN":
                    return await utils.answer(message, self.strings["invalid_token"])
                else:
                    raise ValueError("Invalid response from server", newreq)
            else:
                raise ValueError("Invalid response from server", resp)
        elif resp["status"] != 200:
            raise ValueError("Invalid response from server", resp)

        req = await utils.run_sync(requests.get, self.config["api_url"] + "/cdn/" + resp["message"])
        req.raise_for_status()
        file = BytesIO(req.content)
        file.seek(0)

        if len(args) == 2:
            if args[1] == "file":
                await utils.answer(message, file)
            elif args[1] == "force_file":
                file.name = self.strings["filename"]
                await utils.answer(message, file, force_document=True)
        else:
            img = await utils.run_sync(Image.open, file)
            with BytesIO() as sticker:
                await utils.run_sync(img.save, sticker, "webp")
                sticker.name = "sticker.webp"
                sticker.seek(0)
                try:
                    await utils.answer(message, sticker)
                except telethon.errors.rpcerrorlist.ChatSendStickersForbiddenError:
                    await utils.answer(message, self.strings["cannot_send_stickers"])
                file.close()


def get_markdown(reply):
    if not reply.entities:
        return []

    markdown = []
    for entity in reply.entities:
        md_item = {
            "Type": None,
            "Start": entity.offset,
            "End": entity.offset + entity.length - 1
        }
        if isinstance(entity, telethon.tl.types.MessageEntityBold):
            md_item["Type"] = "bold"
        elif isinstance(entity, telethon.tl.types.MessageEntityItalic):
            md_item["Type"] = "italic"
        elif isinstance(entity, (telethon.tl.types.MessageEntityMention, telethon.tl.types.MessageEntityTextUrl,
                                 telethon.tl.types.MessageEntityMentionName, telethon.tl.types.MessageEntityHashtag,
                                 telethon.tl.types.MessageEntityCashtag, telethon.tl.types.MessageEntityBotCommand,
                                 telethon.tl.types.MessageEntityUrl)):
            md_item["Type"] = "link"
        elif isinstance(entity, telethon.tl.types.MessageEntityCode):
            md_item["Type"] = "code"
        elif isinstance(entity, telethon.tl.types.MessageEntityStrike):
            md_item["Type"] = "stroke"
        elif isinstance(entity, telethon.tl.types.MessageEntityUnderline):
            md_item["Type"] = "underline"
        else:
            logger.warning("Unknown entity: " + str(entity))

        markdown.append(md_item)
    return markdown
