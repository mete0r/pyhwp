# -*- coding: utf-8 -*-
#
#   pyhwp : hwp file format parser in python
#   Copyright (C) 2010-2015 mete0r <mete0r@sarangbang.or.kr>
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


def open_url(context, url):
    ''' open InputStream from a URL.

    :param url: a URL to open an InputStream.
    :returns: an instance of InputStream
    '''

    # see http://wiki.openoffice.org
    #     /wiki/Documentation/DevGuide/UCB/Using_the_UCB_API

    from hwp5.plat._uno.services import css
    css = css.bind(context)
    ucb = css.ucb.UniversalContentBroker('Local', 'Office')
    content_id = ucb.createContentIdentifier(url)
    content = ucb.queryContent(content_id)

    import unohelper
    from com.sun.star.io import XActiveDataSink

    class DataSink(unohelper.Base, XActiveDataSink):
        def setInputStream(self, stream):
            self.stream = stream

        def getInputStream(self):
            return self.stream

    datasink = DataSink()

    from com.sun.star.ucb import Command, OpenCommandArgument2
    openargs = OpenCommandArgument2()
    openargs.Mode = 2  # OpenMode.DOCUMENT
    openargs.Priority = 32768
    openargs.Sink = datasink

    command = Command()
    command.Name = 'open'
    command.Handle = -1
    command.Argument = openargs

    content.execute(command, 0, None)
    return datasink.stream
