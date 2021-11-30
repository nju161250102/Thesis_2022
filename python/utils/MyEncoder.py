from datetime import datetime
import json
from typing import Any

from model import ProjectConfig
from model import Version


class MyEncoder(json.JSONEncoder):

    def default(self, o: Any) -> Any:
        if isinstance(o, datetime):
            return o.strftime("%Y-%m-%d %H:%M")
        elif isinstance(o, ProjectConfig):
            result = o.__dict__
            result["versions"] = [self.default(v) for v in o.versions]
            return result
        elif isinstance(o, Version):
            return o.__dict__
        else:
            return super().default(o)
