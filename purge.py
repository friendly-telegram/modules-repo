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

from .. import loader
import logging

logger = logging.getLogger(__name__)


def register(cb):
    cb(PurgeMod())


class PurgeMod(loader.Module):
    """Deletes your messages"""
    def __init__(self):
        self.name = _("Purge")

    async def purgecmd(self, message):
        """Purge from the replied message"""
        if not message.is_reply:
            await message.edit(_("From where shall I purge?"))
            return
        msgs = []
        from_ids = set()
        async for msg in message.client.iter_messages(
                entity=message.to_id,
                min_id=message.reply_to_msg_id - 1,
                reverse=True):
            msgs += [msg.id]
            from_ids.add(msg.from_id)
            # No async list comprehension in 3.5
        logger.debug(msgs)
        await message.client.delete_messages(message.to_id, msgs)
        await self.allmodules.log("purge", group=message.to_id, affected_uids=from_ids)

    async def delcmd(self, message):
        """Delete the replied message"""
        msgs = [message.id]
        if not message.is_reply:
            msg = await message.client.iter_messages(message.to_id, 1, max_id=message.id).__anext__()
        else:
            msg = await message.get_reply_message()
        msgs.append(msg.id)
        logger.debug(msgs)
        await message.client.delete_messages(message.to_id, msgs)
        await self.allmodules.log("delete", group=message.to_id, affected_uids=[msg.from_id])
