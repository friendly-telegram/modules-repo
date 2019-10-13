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

import asyncio
import time
import logging
from PIL import Image
from io import BytesIO
from telethon.tl import functions
from ast import literal_eval
from .. import loader, utils

logger = logging.getLogger(__name__)


def register(cb):
    cb(AutoProfileMod())


class AutoProfileMod(loader.Module):
    """Automatic stuff for your profile :P"""
    def __init__(self):
        self.name = _("Automatic Profile")
        self.bio_enabled = False
        self.name_enabled = False
        self.pfp_enabled = False
        self.pfp_remove_latest = None
        self.raw_bio = None
        self.raw_name = None
        self.pfp_degree = 0

    async def client_ready(self, client, db):
        self.client = client

    async def autopfpcmd(self, message):
        """Rotates your profile picture every n seconds with x degrees, usage:
           .autopfp <timeout> <degrees> <remove previous (last pfp)>

           Timeout - seconds
           Degrees - 60, -10, etc
           Remove last pfp - True/False, case sensitive"""

        if not await self.client.get_profile_photos(await self.client.get_me(), limit=1):
            return await utils.answer(message, _("<b>You don't have profile pic set.</b>"))

        msg = utils.get_args(message)
        if len(msg) != 3:
            return await utils.answer(message, _("<b>Autopfp requires three args. See the help for syntax.</b>"))

        try:
            timeout_autopfp = int(msg[0])
        except ValueError as e:
            logger.warning(str(e))
            return await utils.answer(message, _("<b>Wrong time.</b>"))

        try:
            degrees = int(msg[1])
        except ValueError as e:
            logger.warning(str(e))
            return await utils.answer(message, _("<b>Wrong degrees value.</b>"))

        try:
            delete_previous = literal_eval(msg[2])
        except (ValueError, SyntaxError):
            return await utils.answer(message, _("<b>Please pass True or False for previous pfp removing.</b>"))

        me = await self.client.get_me()
        pfp = await self.client.download_profile_photo(me, file=bytes)
        raw_pfp = Image.open(BytesIO(pfp))

        self.pfp_remove_latest = delete_previous
        self.pfp_enabled = True
        await utils.answer(message, "<b>Successfully enabled autopfp.</b>")

        while self.pfp_enabled:
            self.pfp_degree += degrees
            rotated = raw_pfp.rotate(self.pfp_degree)
            buf = BytesIO()
            rotated.save(buf, format='JPEG')
            buf.seek(0)

            if self.pfp_remove_latest:
                await self.client(functions.photos.DeletePhotosRequest(
                    await self.client.get_profile_photos(await self.client.get_me(), limit=1)
                ))

            await self.client(functions.photos.UploadProfilePhotoRequest(
                await self.client.upload_file(buf)
            ))
            await asyncio.sleep(timeout_autopfp)

    async def stopautopfpcmd(self, message):
        """ Stop autobio cmd."""

        if self.pfp_enabled is False:
            return await utils.answer(message, _("<b>Autopfp is already disabled.</b>"))
        else:
            self.pfp_enabled = False
            self.pfp_degree = 0
            self.pfp_remove_latest = None

            await self.client(functions.photos.DeletePhotosRequest(
                await self.client.get_profile_photos(await self.client.get_me(), limit=1)
            ))
            await utils.answer(message, _("<b>Successfully disabled autobio, removing last profile pic.</b>"))

    async def autobiocmd(self, message):
        """ Automatically changes your Telegram's bio with current time, usage:
            .autobio <timeout, seconds> '<message, time as {time}>'"""

        msg = utils.get_args(message)
        if len(msg) != 2:
            return await utils.answer(message, _("<b>AutoBio requires two args.</b>"))
        else:
            raw_bio = msg[1]
            try:
                timeout_autobio = int(msg[0])
            except ValueError as e:
                logger.warning(str(e))
                return await utils.answer(message, _("<b>Wrong time.</b>"))
        if '{time}' not in raw_bio:
            return await utils.answer(message, _("<b>You haven't specified time position/Wrong format.</b>"))

        self.bio_enabled = True
        self.raw_bio = raw_bio
        await utils.answer(message, "<b>Successfully enabled autobio.</b>")

        while self.bio_enabled is True:
            current_time = time.strftime("%H:%M")
            bio = raw_bio.format(time=current_time)
            await self.client(functions.account.UpdateProfileRequest(
                about=bio
            ))
            await asyncio.sleep(timeout_autobio)

    async def stopautobiocmd(self, message):
        """ Stop autobio cmd."""

        if self.bio_enabled is False:
            return await utils.answer(message, _("<b>Autobio is already disabled.</b>"))
        else:
            self.bio_enabled = False
            await utils.answer(message, _("<b>Successfully disabled autobio, setting bio to without time.</b>"))
            await self.client(functions.account.UpdateProfileRequest(
                about=self.raw_bio.format(time="")
            ))

    async def autonamecmd(self, message):
        """ Automatically changes your Telegram name with current time, usage:
            .autoname <timeout, seconds> '<message, time as {time}>'"""

        msg = utils.get_args(message)
        if len(msg) != 2:
            return await utils.answer(message, _("<b>AutoName requires two args.</b>"))
        else:
            raw_name = msg[1]
            try:
                timeout_autoname = int(msg[0])
            except ValueError as e:
                logger.error(str(e))
                return await utils.answer(message, _("<b>Wrong time.</b>"))
        if "{time}" not in raw_name:
            return await utils.answer(message, _("<b>You haven't specified time position/Wrong format.</b>"))

        self.name_enabled = True
        self.raw_name = raw_name
        await utils.answer(message, _("<b>Successfully enabled autoname.</b>"))

        while self.name_enabled is True:
            current_time = time.strftime("%H:%M")
            name = raw_name.format(time=current_time)
            await self.client(functions.account.UpdateProfileRequest(
                first_name=name
            ))
            await asyncio.sleep(timeout_autoname)

    async def stopautonamecmd(self, message):
        """ Stop autoname cmd."""

        if self.name_enabled is False:
            return await utils.answer(message, _("<b>Autoname is already disabled.</b>"))
        else:
            self.name_enabled = False
            await utils.answer(message, _("<b>Successfully disabled autoname, setting name to without time.</b>"))
            await self.client(functions.account.UpdateProfileRequest(
                first_name=self.raw_name.format(time="")
            ))
