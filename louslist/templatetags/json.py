from django import template
from typing import Dict, List, Union
import json

register = template.Library()


@register.simple_tag
def to_json(value: Union[Dict, List]) -> str:
    return json.dumps(value)
