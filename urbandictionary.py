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

import asyncurban
from .. import loader, utils

logger = logging.getLogger(__name__)


def register(cb):
    cb(UrbanDictionaryMod())


class UrbanDictionaryMod(loader.Module):
    """Define word meaning using UrbanDictionary."""
    def __init__(self):
        self.name = _("Urban Dictionary")
        self.urban = asyncurban.UrbanDictionary()

    async def urbancmd(self, message):
        """Define word meaning. Usage:
            .urban <word(s)>"""

        args = utils.get_args_raw(message)

        if not args:
            return await utils.answer(message, _("<b>Provide a word(s) to define.</b>"))

        try:
            definition = await self.urban.get_word(args)
        except asyncurban.WordNotFoundError:
            return await utils.answer(message, _("<b>Couldn't find definition for that.</b>"))

        await utils.answer(message, _("<b>Text</b>: <code>{}</code>\n<b>Meaning</b>: <code>{}\n<b>Example</b>: <code>"
                                      "{}</code>").format(definition.word, definition.definition, definition.example))
