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

from search_engine_parser import GoogleSearch

from .. import loader, utils

logger = logging.getLogger(__name__)


def register(cb):
    cb(GoogleSearchMod())


class GoogleSearchMod(loader.Module):
    """Make a Google search, right in your chat!"""
    def __init__(self):
        self.name = _("Search Engine")

    async def googlecmd(self, message):
        """Shows Google search results."""
        if len(utils.get_args_raw(message)) == 0:
            text = (await message.get_reply_message()).message
        else:
            text = utils.get_args_raw(message.message)
        if len(text) == 0:
            await message.edit(_("Unfortunately, I can't Google nothing."))
            return
        # TODO: add ability to specify page number.
        search_args = (str(text), 1)
        gsearch = GoogleSearch()
        gresults = await gsearch.async_search(*search_args)
        msg = ""
        for i in range(len(gresults["titles"])):
            try:
                title = gresults["titles"][i]
                link = gresults["links"][i]
                desc = gresults["descriptions"][i]
                msg += f"<p><a href='{link}'>{title}</a></p>\
                \n<code>{desc}</code>\n\n"
            except IndexError:
                break
        if msg == "":
            await utils.answer(message, _(f"Could not find anything about <code>{text}</code> on Google."))
            return
        else:
            await utils.answer(message, _(f"These came back from a Google search for <code>{text}</code>:\
            \n\n{msg}"))
