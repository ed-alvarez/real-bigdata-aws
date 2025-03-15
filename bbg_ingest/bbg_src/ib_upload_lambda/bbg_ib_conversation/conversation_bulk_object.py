"""
This object holds a list of each item in a bbg_ib_conversation.
it is used for the es Bulk upload process
"""
import logging
from typing import Dict, List

from bbg_helpers.es_bbg_ib_index import BBG_IB

from shared.shared_src.utils import get_size

log = logging.getLogger()


class ibConversation:
    def __init__(self) -> None:
        self._list_of_ib_items: List[Dict] = list()
        self._msg_count: int = 0
        self._msg_list_size: int = 0

    @property
    def listOfIBItems(self) -> List[Dict]:
        return self._list_of_ib_items

    @property
    def ibListCount(self) -> int:
        return self._msg_count

    @property
    def ibListSize(self):
        return self._msg_list_size

    def add_ib(self, bbg_ib: BBG_IB) -> None:
        self._list_of_ib_items.append(bbg_ib.to_dict())
        self._msg_count += 1
        self._msg_list_size += get_size(bbg_ib)
        return
