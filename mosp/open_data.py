###############################################################################
#Copyright 2014 CHOICE Online Marketing Group
#
#This file is part of MosP.
#
#MosP is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
#MosP is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with MosP.  If not, see <http://www.gnu.org/licenses/>.
###############################################################################

import json
import urllib2

"""
class OpenData
"""
class OpenData:
    """
    Constructor
    """
    def __init__(self, url, fname):
        self._url = url
        self._fname = fname
        self._GET = {}
        self.data = {}

    def add_get(self, key, value):
        self._GET[key] = value

    @property
    def url(self):
        rval = self._url + self._fname
        if self._GET:
            rval += '?'
            first_loop = True
            for key in self._GET:
                if not first_loop:
                    rval += '&'
                rval += key + '=' + self._GET[key]
                first_loop = False
        
        return rval

    @url.setter
    def url(self, new_url):
        self._url = new_url

    @property
    def json(self):
        return json.dumps(self.data)

    def refresh(self):
        url_data = urllib2.urlopen(self.url).read()
        self.data = json.loads(url_data)
