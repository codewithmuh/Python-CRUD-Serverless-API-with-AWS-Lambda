import json
import JSONEncoder
from decimal import Decimal


class CustomEncoder(json, JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return floadt(obj)

        return json.JSONEncoder.default(self, obj)   