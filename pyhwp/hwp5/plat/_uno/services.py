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


def create_service(context, name, *args):
    sm = context.ServiceManager
    if len(args) > 0:
        return sm.createInstanceWithArgumentsAndContext(name, args, context)
    else:
        return sm.createInstanceWithContext(name, context)


class Namespace(object):
    def __init__(self, dotted_name):
        self.dotted_name = dotted_name

    def __getattr__(self, name):
        return Namespace(self.dotted_name + '.' + name)

    def __call__(self, context, *args):
        return create_service(context, self.dotted_name, *args)

    def bind(self, context):
        return ContextBoundNamespace(self, context)


class ContextBoundNamespace(object):

    def __init__(self, namespace, context):
        self.namespace = namespace
        self.context = context

    def __getattr__(self, name):
        obj = getattr(self.namespace, name, None)
        if isinstance(obj, Namespace):
            return obj.bind(self.context)
        return obj

    def __call__(self, *args):
        return self.namespace(self.context, *args)

    def __iter__(self):
        context = self.context
        sm = context.ServiceManager
        prefix = self.dotted_name + '.'
        for name in sm.AvailableServiceNames:
            if name.startswith(prefix):
                basename = name[len(prefix):]
                if basename.find('.') == -1:
                    yield basename


css = Namespace('com.sun.star')
