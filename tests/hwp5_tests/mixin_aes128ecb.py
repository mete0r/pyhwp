# -*- coding: utf-8 -*-
#
#   pyhwp : hwp file format parser in python
#   Copyright (C) 2010-2019 mete0r <mete0r@sarangbang.or.kr>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals
from binascii import a2b_base64
from binascii import a2b_hex


class AES128ECBTestMixin(object):

    def test_decrypt(self):
        if self.aes128ecb is None:
            return

        record = a2b_base64(
            b'HAAAEJtiLk+dnZ2dnZ2dnRwcHCQcXxxeX21fbV9sX2hfG19vX2lkU2RdZCdkJWRc'
            b'ZFwiZiJgIhQiFiJew/fDhsPSk9Cvma+fr+uv7q+Wr5mvnK+bSn9Kf0p7SnkBOAE3'
            b'AR8rK6srK+rq6urq6urq6urq6urq6uqSkpJWYmJiYmJiYmJiYmJiYszMzMzMzMzM'
            b'zMzMzMzMzAICAgICAgICAgICApaWlpaWlpaWlpaWlpaWlpalpaWlpSMjIyMjI8/P'
            b'z8/Pz8/Pz8/Pz8/Pz8+pqampqampqampqakVFRUVFRUVFRUVFRUOJAkJCQkEBAQE'
            b'BASFnp6enkZGRkZGRkZGRkZ8fHw2RPqIfYOxPACfuEgIRMP5u9esyqV3d9tqcqVX'
            b'RZjPmx89Yr0Hctu4frmCoKRL2B3UsBcpfuy9e7Q1hj30cQuRXp+XaO496hIPRG6w'
            b'Z9nxqgVrbct7V/H/l2NdR5VLVbTDVFxH8EQQUVWVTXR8oyj6yTMMyP1asPQKEMb+'
            b'pUMTMOoZrinnXGSEdHUQ+XPFZTvy4bs/658pQq6SAHktX57QFg354hBw2USpwhM/'
            b'FugQ4w6wvsEQfgTwKnPc3M4AL+AZmltDz+u0AVL2M3IbulpCvk3zpGN1vj8f5dzc'
            b'eJ7sEw5GGeLFW611F023JaSzW0M='
        )
        key = a2b_hex('38004300420032003200330037004400')
        ciphertext = record[4 + 256:]  # record header (4), record payload(256)
        plaintext = a2b_base64(
            b'c2JIYNRmYGhgYWBgYGRgYAZiEA0EziwJrEwMKcmpxWAuEDABYUpOfjKCX8BQyZDB'
            b'UM5QwKDA4HNxyaEdl2p2KjCwHI+5qsBgsOfNZQUGi90yBxUYOI7JnGg9fmLTk016'
            b'DLwMLiwNYCNA9riyODDBzHvBzMAAwkFAHAEVlVgGkmVjcAeqg7klD+RYBgd5mEth'
            b'+kG0J0cDU8cLBoY7HowMFooMYKwixsAwRwCBYeq9OA5AvAoEmkDX/AeCIGZzJmlG'
            b'RrA4uvwP/QdAt5kDXQaR9+Z4APZDJysEEifizsLACApFFqCLYAAApD7Q74YBAAAA'
        )

        decrypted = self.aes128ecb.decrypt(key, ciphertext)
        self.assertEqual(plaintext, decrypted)
