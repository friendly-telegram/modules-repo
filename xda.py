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
import random


def register(cb):
    cb(XDAMod())


RANDOM_WORDS = {"sur": 6, "Sir": 6, "bro": 6, "yes": 5, "no": 5, "bolte": 2, "bolit": 2, "bholit": 3, "volit": 3,
                "mustah": 4, "fap": 5, "lit": 3, "lmao": 6, "iz": 7, "jiosim": 8, "ijo": 4, "nut": 7, "workz": 4,
                "workang": 4, "flashabl zip": 6, "bateri": 6, "bacup": 6, "bad englis": 5, "sar": 5, "treble wen": 2,
                "gsi": 6, "fox bag": 3, "bag fox": 3, "fine": 4, "bast room": 5, "fax": 3, "trable": 3, "kenzo": 4,
                "plz make room": 3, "andreid pai": 2, "when": 4, "port": 5, "mtk": 3, "send moni": 3, "bad rom": 2,
                "dot": 4, "rr": 4, "linage": 4, "arrows": 4, "kernal": 4}

# Workaround for 3.5
WORDS_WEIGHTED = [word for word, count in RANDOM_WORDS.items() for i in range(count)]


class XDAMod(loader.Module):
    """Gibes bholte bro"""
    def __init__(self):
        self.config = loader.ModuleConfig("XDA_RANDOM_WORDS", RANDOM_WORDS, "Random words from XDA as dict & weight")
        self.name = "XDA"

    async def xdacmd(self, message):
        """Send random XDA posts"""
        length = random.randint(3, 10)
        # Workaround for 3.5
        string = [random.choice(WORDS_WEIGHTED) for dummy in range(length)]

        # Unsupported in python 3.5
        # string = random.choices(self.config["XDA_RANDOM_WORDS"], weights=self.config["XDA_WEIGHT_WORDS"], k=length)

        random.shuffle(string)
        await message.edit(" ".join(string))
