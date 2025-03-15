"""
This object holds a list of bbg_messages
it is used for the es Bulk upload process
"""


from typing import Dict, List

from bbg_helpers.es_bbg_msg_index import BBG_MSG

from shared.shared_src.utils import get_size


class msg_bulk_collection:
    def __init__(self):
        self._list_of_msg: List[Dict] = list()
        self._msg_count: int = 0
        self._msg_list_size: int = 0

    @property
    def listOfMSGItems(self) -> List[Dict]:
        return self._list_of_msg

    @property
    def msgListCount(self) -> int:
        return self._msg_count

    @property
    def msgListSize(self) -> int:
        return self._msg_list_size

    def add_msg(self, bbg_msg: BBG_MSG) -> None:
        self._list_of_msg.append(bbg_msg.to_dict())
        self._msg_count += 1
        self._msg_list_size += get_size(bbg_msg)
        return
