#-*- coding: utf-8 -*-
# suggestion.py
# Copyright (C) 2014 Cyril Peponnet cyril@peponnet.fr
# inspired by https://github.com/isometry/alfredworkflows/
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import json
import re
import sys

from os import path
from time import time

import string

class FileCache:
    def __init__(self,files):
        self.filecache = {}
        self.grabFiles(files)

    def grabFiles(self, files):
        for afile in files:
            if not path.isfile(path.expanduser(afile)):
                continue
            if not self.filecache.has_key(afile):
                try:
                    f = open(path.expanduser(afile), "r")
                    self.filecache[afile] = string.split(f.read(), '\n')
                    f.close()
                except:
                    pass

class Hosts(object):
    def __init__(self, user=None):
        self.hosts = []
        self.user = user

    def add(self, host):
        if host not in self.hosts:
            self.hosts.append(host)

    def update(self, hosts):
        if not hosts:
            return
        for host in hosts:
            self.add(host)

    def item(self, host):
        _arg = self.user and '@'.join([self.user, host]) or host
        return  {"title":_arg, 'icon': 'ssh.png'}

    def filter(self, _filter=(lambda x: True)):
        items=[]
        for host in self.hosts:
            if _filter(host):
                items.append(self.item(host))
        return items

def fetch_ssh_config(_cache, key):
    if key in _cache.keys():
        results = set()
        results.update(
            x for line in _cache[key]
            if line[:5].lower() == 'host '
            for x in line.split()[1:]
            if not ('*' in x or '?' in x or '!' in x)
        )
        return results

def fetch_known_hosts(_cache, key):
    if key in _cache.keys():
        results = set()
        results.update(
            x for line in _cache[key]
            if line.strip() and not line.startswith('|')
            for x in line.split()[0].split(',')
        )
        return results

def fetch_hosts(_cache, key):
    if key in _cache.keys():
        results = set()
        results.update(
            x for line in _cache[key]
            if not line.startswith('#')
            for x in line.split()[1:]
        )
        results.discard('broadcasthost')
        return results

def fetch_bonjour(_service, alias='Bonjour', timeout=0.1):
    results = set()
    try:
        from pybonjour import DNSServiceBrowse, DNSServiceProcessResult
        from select import select
        bj_callback = lambda s, f, i, e, n, t, d: results.add('%s.%s' % (n.lower(), d[:-1]))
        bj_browser = DNSServiceBrowse(regtype=_service, callBack=bj_callback)
        select([bj_browser], [], [], timeout)
        DNSServiceProcessResult(bj_browser)
        bj_browser.close()
    except ImportError:
        pass
    return results

if __name__ == "__main__":
    if len(sys.argv) == 2:
        if '@' in sys.argv[1]:
            (user, host) = sys.argv[1].split('@',1)
        else:
            (user, host) = (None, sys.argv[1])
    else:
            (user, host) = (None, ".")

    host_chars = (('\\.' if x is '.' else x) for x in list(host))
    pattern = re.compile('.*?\b?'.join(host_chars), flags=re.IGNORECASE)

    hosts = Hosts(user=user)
    _cache=FileCache(['~/.ssh/config','~/.ssh/known_hosts','/etc/hosts'])

    for results in (
        fetch_ssh_config(_cache.filecache,'~/.ssh/config'),
        fetch_known_hosts(_cache.filecache,'~/.ssh/known_hosts'),
        fetch_hosts(_cache.filecache,'/etc/hosts'),
        fetch_bonjour('_ssh._tcp')
    ):
        hosts.update(results)

    print json.dumps(hosts.filter(pattern.search))