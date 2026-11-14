import json
import os

_CURR = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(_CURR, "module5.json"), "r", encoding="utf-8") as _f:
    _DATA = json.load(_f)

MODULE_ID = _DATA["module_id"]
MODULE_TITLE = _DATA["title"]
MODULE_DESC = _DATA["description"]
TOPICS = _DATA["topics"]
QUESTIONS = _DATA["questions"]
