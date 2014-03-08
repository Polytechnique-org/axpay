# -*- coding: utf-8 -*-
# Copyright (c) 2013 AX. All rights reserved.

import os
import collections
import ConfigParser


SOURCE_DEFAULT = 'default'
SOURCE_FILE = 'file'
SOURCE_ENV = 'environment'

ConfigEntry = collections.namedtuple('ConfigEntry',
    ['key', 'section', 'entry', 'env', 'value', 'source'])


class Config(object):
    def __init__(self, project_name, *config_files):
        assert project_name == project_name.lower(), "Project name should be lower case (got %s)" % project_name
        self.project_name = project_name
        self.config_files = config_files

        self.seen_entries = {}
        self.config_data = self._open_config_files()

    def extra_config_file_path(self):
        key = '%s_CONFIG' % (self.project_name,)
        return os.environ.get(key)

    def _open_config_files(self):
        parser = ConfigParser.SafeConfigParser()
        parser.read(self.config_files)

        extra_file = self.extra_config_file_path()
        if extra_file:
            parser.read(extra_file)
        return parser

    def get(self, key, default):
        if key in self.seen_entries:
            return self.seen_entries[key].value

        value = default
        source = SOURCE_DEFAULT

        if '.' in key:
            section, subkey = key.split('.', 1)
            env_key = ('%s_%s_%s' % (self.project_name, section, subkey)).upper()
        else:
            section = self.project_name
            subkey = key
            env_key = ('%s_%s' % (self.project_name, subkey)).upper()

        try:
            value = self.config_data.get(section or self.project_name, subkey)
        except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
            pass
        else:
            source = SOURCE_FILE

        try:
            value = os.environ[env_key]
        except KeyError:
            pass
        else:
            source = SOURCE_ENV

        self.seen_entries[key] = ConfigEntry(
            key=key,
            section=section,
            entry=subkey,
            env=env_key,
            value=value,
            source=source,
        )
        return value

    def getlist(self, key, default=''):
        value = self.get(key, default)
        return [e.strip() for e in value.split(',')]

    def getbool(self, key, default=False):
        value = self.get(key, default)
        return str(value).lower() in ['1', 'true', 'on', 'yes']
