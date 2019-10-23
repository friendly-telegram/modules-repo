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
import ast
import time
import logging
from io import BytesIO
from telethon.tl import functions
from .. import loader, utils

logger = logging.getLogger(__name__)

try:
    from PIL import Image
except ImportError:
    pil_installed = False
else:
    pil_installed = True


def register(cb):
    cb(AutoProfileMod())


class AutoProfileMod(loader.Module):
    """Automatic stuff for your profile :P"""
    def __init__(self):
        self.name = _("Automatic Profile")
        self.bio_enabled = False
        self.name_enabled = False
        self.pfp_enabled = False
        self.raw_bio = None
        self.raw_name = None

    async def client_ready(self, client, db):
        self.client = client

    async def autopfpcmd(self, message):
        """Rotates your profile picture every n seconds with x degrees, usage:
           .autopfp <timeout> <degrees> <remove previous (last pfp)>

           Timeout - seconds
           Degrees - 60, -10, etc
           Remove last pfp - True/False, case sensitive"""

        if not pil_installed:
            return await utils.answer(message, _("<b>You don't have PIL (Pillow) installed.</b>"))

        if not await self.client.get_profile_photos("me", limit=1):
            return await utils.answer(message, _("<b>You don't have a profile pic set.</b>"))

        msg = utils.get_args(message)
        if len(msg) != 3:
            return await utils.answer(message, _("<b>Autopfp requires three args. See the help for syntax.</b>"))

        try:
            timeout_autopfp = int(msg[0])
        except ValueError:
            return await utils.answer(message, _("<b>Wrong time.</b>"))

        try:
            degrees = int(msg[1])
        except ValueError:
            return await utils.answer(message, _("<b>Wrong degrees value.</b>"))

        try:
            delete_previous = ast.literal_eval(msg[2])
        except (ValueError, SyntaxError):
            return await utils.answer(message, _("<b>Please pass True or False for previous pfp removal.</b>"))

        with BytesIO() as pfp:
            await self.client.download_profile_photo("me", file=pfp)
            raw_pfp = Image.open(pfp)

            self.pfp_enabled = True
            pfp_degree = 0
            await self.allmodules.log("start_autopfp")
            await utils.answer(message, "<b>Successfully enabled autopfp.</b>")

            while self.pfp_enabled:
                pfp_degree = (pfp_degree + degrees) % 360
                rotated = raw_pfp.rotate(pfp_degree)
                with BytesIO() as buf:
                    rotated.save(buf, format="JPEG")
                    buf.seek(0)

                    if delete_previous:
                        await self.client(functions.photos.
                                          DeletePhotosRequest(await self.client.get_profile_photos("me", limit=1)))

                    await self.client(functions.photos.UploadProfilePhotoRequest(await self.client.upload_file(buf)))
                    buf.close()
                await asyncio.sleep(timeout_autopfp)

    async def stopautopfpcmd(self, message):
        """Stop autobio cmd."""

        if self.pfp_enabled is False:
            return await utils.answer(message, _("<b>Autopfp is already disabled.</b>"))
        else:
            self.pfp_enabled = False

            await self.client(functions.photos.DeletePhotosRequest(
                await self.client.get_profile_photos("me", limit=1)
            ))
            await self.allmodules.log("stop_autopfp")
            await utils.answer(message, _("<b>Successfully disabled autobio, removing last profile pic.</b>"))

    async def autobiocmd(self, message):
        """Automatically changes your account's bio with current time, usage:
            .autobio <timeout, seconds> '<message, time as {time}>'"""

        msg = utils.get_args(message)
        if len(msg) != 2:
            return await utils.answer(message, _("<b>AutoBio requires two args.</b>"))
        else:
            raw_bio = msg[1]
            try:
                timeout_autobio = int(msg[0])
            except ValueError:
                return await utils.answer(message, _("<b>Wrong time.</b>"))
        if "{time}" not in raw_bio:
            return await utils.answer(message, _("<b>You haven't specified time position/Wrong format.</b>"))

        self.bio_enabled = True
        self.raw_bio = raw_bio
        await self.allmodules.log("start_autobio")
        await utils.answer(message, _("<b>Successfully enabled autobio.</b>"))

        while self.bio_enabled is True:
            current_time = time.strftime("%H:%M")
            bio = raw_bio.format(time=current_time)
            await self.client(functions.account.UpdateProfileRequest(
                about=bio
            ))
            await asyncio.sleep(timeout_autobio)

    async def stopautobiocmd(self, message):
        """Stop autobio cmd."""

        if self.bio_enabled is False:
            return await utils.answer(message, _("<b>Autobio is already disabled.</b>"))
        else:
            self.bio_enabled = False
            await self.allmodules.log("stop_autobio")
            await utils.answer(message, _("<b>Successfully disabled autobio, setting bio to without time.</b>"))
            await self.client(functions.account.UpdateProfileRequest(
                about=self.raw_bio.format(time="")
            ))

    async def autonamecmd(self, message):
        """Automatically changes your Telegram name with current time, usage:
            .autoname <timeout, seconds> '<message, time as {time}>'"""

        msg = utils.get_args(message)
        if len(msg) != 2:
            return await utils.answer(message, _("<b>AutoName requires two args.</b>"))
        else:
            raw_name = msg[1]
            try:
                timeout_autoname = int(msg[0])
            except ValueError:
                return await utils.answer(message, _("<b>Wrong time.</b>"))
        if "{time}" not in raw_name:
            return await utils.answer(message, _("<b>You haven't specified time position/Wrong format.</b>"))

        self.name_enabled = True
        self.raw_name = raw_name
        await self.allmodules.log("start_autoname")
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
            await self.allmodules.log("stop_autoname")
            await utils.answer(message, _("<b>Successfully disabled autoname, setting name to without time.</b>"))
            await self.client(functions.account.UpdateProfileRequest(
                first_name=self.raw_name.format(time="")
            ))

    async def delpfpcmd(self, message):
        """ Remove x profile pic(s) from your profile.
        .delpfp <pfps count/unlimited - remove all>"""

        args = utils.get_args(message)
        if not args:
            return await utils.answer(message, _("<b>Please specify number of profile pics to remove.</b>"))
        if args[0].lower() == "unlimited":
            pfps_count = None
        else:
            try:
                pfps_count = int(args[0])
            except ValueError:
                return await utils.answer(message, _("<b>Wrong amount of pfps.</b>"))
            if pfps_count <= 0:
                return await utils.answer(message, _("<b>Please provide positive number of"
                                                     + " profile pictures to remove.</b>"))

        await self.client(functions.photos.DeletePhotosRequest(await self.client.get_profile_photos("me",
                                                                                                    limit=pfps_count)))

        if pfps_count is None:
            pfps_count = _("all")
        await self.allmodules.log("delpfp")
        await utils.answer(message, _("<b>Removed </b><code>{}</code><b> profile pic(s).</b>".format(str(pfps_count))))
