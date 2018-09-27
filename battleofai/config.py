import json
import sys


class Config(dict):
    def from_json_file(self, path):
        with open(path, 'r', encoding="utf-8") as f:
            config = json.load(f)
            self.update(**config)

    def from_python_file(self, path):
        path = path.split('/')
        module = path.pop().rstrip('.py')
        location = '/'.join(path)

        sys.path.insert(0, location)
        config = __import__(module)

        properties = {i: config.__dict__[i] for i in dir(config) if not i.startswith('__')}

        self.update(**properties)

    @property
    def username(self):
        return self.get("username")

    @property
    def password(self):
        return self.get("password")
