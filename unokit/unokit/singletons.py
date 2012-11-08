# -*- coding: utf-8 -*-
#
#   pyhwp : hwp file format parser in python
#   Copyright (C) 2010 mete0r@sarangbang.or.kr
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

def get_singleton(name):
    import unokit.contexts
    context = unokit.contexts.get_current()
    return context.getValueByName('/singletons/'+name)


def iter_singleton_names():
    import unokit.contexts
    context = unokit.contexts.get_current()
    names = (name[len('/singletons/'):]
             for name in context.ElementNames
             if (name.startswith('/singletons/')
                 and not name.endswith('/service')))
    return names


class NamespaceNode(object):
    def __init__(self, dotted_name):
        self.dotted_name = dotted_name

    def __getattr__(self, name):
        import unokit.contexts
        context = unokit.contexts.get_current()
        dotted_name = self.dotted_name + '.' + name
        full_name = '/singletons/' + dotted_name
        if full_name in context.ElementNames:
            return context.getValueByName(full_name)
        return NamespaceNode(self.dotted_name + '.' + name)

    def __iter__(self):
        prefix = self.dotted_name + '.'
        for name in iter_singleton_names():
            if name.startswith(prefix):
                basename = name[len(prefix):]
                if basename.find('.') == -1:
                    yield basename


css = NamespaceNode('com.sun.star')
