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
import speedtest

from .. import loader, utils

logger = logging.getLogger(__name__)


def register(cb):
    cb(SpeedtestMod())


class SpeedtestMod(loader.Module):
    """Uses speedtest.net"""
    def __init__(self):
        self.name = _("Speedtest")

    async def speedtestcmd(self, message):
        """Tests your internet speed"""
        await utils.answer(message, _("<code>Running speedtest...</code>"))
        args = utils.get_args(message)
        servers = []
        for server in args:
            try:
                servers += [int(server)]
            except ValueError:
                logger.warning("server failed")
        results = await utils.run_sync(self.speedtest, servers)
        ret = _("<b>Speedtest Results:</b>") + "\n\n"
        ret += _("<b>Download:</b> <code>{} MiB/s</code>").format(round(results["download"] / 2**20, 2)) + "\n"
        ret += _("<b>Upload:</b> <code>{} MiB/s</code>").format(round(results["upload"] / 2**20, 2)) + "\n"
        ret += _("<b>Ping:</b> <code>{} milliseconds</code>").format(round(results["ping"], 2)) + "\n"
        await utils.answer(message, ret)

    def speedtest(self, servers):
        speedtester = speedtest.Speedtest()
        speedtester.get_servers(servers)
        speedtester.get_best_server()
        speedtester.download(threads=None)
        speedtester.upload(threads=None)
        return speedtester.results.dict()
