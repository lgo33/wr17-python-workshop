import configparser
import json


class JSONConfig(configparser.RawConfigParser):
    def __init__(self, filename):
        self.filename = filename
        super().__init__()
        self.optionxform = str
        self.read(self.filename)

    def save(self):
        with open(self.filename, 'w') as cfgfile:
            self.write(cfgfile)

    def get(self, *args, **kwargs):
        try:
            return json.loads(super().get(*args, **kwargs))
        except json.JSONDecodeError:
            return super().get(*args, **kwargs)

    def set(self, section, value, *args, **kwargs):
        return super().set(section, json.dumps(value), *args, **kwargs)