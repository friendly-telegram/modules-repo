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
from requests import get

logger = logging.getLogger(__name__)


def register(cb):
    cb(LetMeGoogleThatForYou())


class LetMeGoogleThatForYou(loader.Module):
    """Let me Google that for you, coz you too lazy to do that yourself."""
    def __init__(self):
        self.name = _("LetMeGoogleThatForYou")

    async def lmgtfycmd(self, message):
        """Use in reply to another message or as .lmgtfy <text>"""
        if len(utils.get_args_raw(message)) == 0:
            text = (await message.get_reply_message()).message
        else:
            text = utils.get_args_raw(message.message)
        if len(text) == 0:
            await message.edit(_("I need something to Google for them."))
            return
        query_encoded = text.replace(" ", "+")
        lfy_url = f"http://lmgtfy.com/?s=g&iie=1&q={query_encoded}"
        payload = {'format': 'json', 'url': lfy_url}
        r = get('http://is.gd/create.php', params=payload)
        await utils.answer(message, _(f"Here you go, help yourself.\
        \n<p><a href='{r.json()['shorturl']}'>{text}</a></p>"))
