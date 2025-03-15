"""
An object to hold the group of bbg_ib_conversation participants at any given time
this object is populated sequentially throughout the bbg_ib_conversation so at any time holds the participants
relavant to the message being processed

Getting the to list extracts all the participants who are not the message from user

"""
import logging
from typing import List

from bbg_helpers.es_bbg_ib_index import bloomberg_id

log = logging.getLogger()


class msgToGroup:
    def __init__(self) -> None:
        self._user_list: List[bloomberg_id] = list()

    @property
    def userList(self):
        return self._user_list

    # Add a user to the participants for a Message or Attachment
    def add_user(self, new_user: bloomberg_id) -> None:
        user: bloomberg_id
        if not [user for user in self._user_list if user.loginname == new_user.loginname]:
            try:
                self._user_list.append(new_user)
            except Exception as ex:
                log.exception(ex)
        else:
            log.debug(f"User {new_user} already in list")
        return

    # Remove a user from the participants list for a Message or an Attachment
    def remove_user(self, user: bloomberg_id) -> None:

        find_user: bloomberg_id
        for find_user in self._user_list:
            if find_user.loginname == user.loginname:
                try:
                    self._user_list.remove(find_user)
                except ValueError as ex:
                    log.debug(f"{find_user.loginname} not found in list")
                    pass
        return

    def get_to_list(self, messageFrom: bloomberg_id) -> List[bloomberg_id]:
        user: bloomberg_id
        to_list: List[bloomberg_id] = [user for user in self._user_list if user.loginname != messageFrom.loginname]
        if not to_list:
            log.debug("No Users in the TO list which is OK for the first message but odd after that!")
            return []
        return to_list


if __name__ == "__main__":

    def test_msgToList():
        user = bloomberg_id()
        user.loginname = "BJNIXON"
        user.firstname = "BEN"
        user.lastname = "NIXON"
        user.companyname = "JEFFERIES INTERNATIO"
        user.emailaddress = "BJNIXON@Bloomberg.net"
        user.domain = "bloomberg.net"

        user_1 = bloomberg_id()
        user_1.loginname = "LUDOCOHEN"
        user_1.firstname = "LUDOVIC"
        user_1.lastname = "COHEN"
        user_1.companyname = "JEFFERIES INTERNATIO"
        user_1.emailaddress = "LUDOCOHEN@Bloomberg.net"
        user_1.domain = "bloomberg.net"

        user_2 = bloomberg_id()
        user_2.loginname = "SEANSYSTEM2"
        user_2.firstname = "SEAN"
        user_2.lastname = "OLDFIELD"
        user_2.loginname = "25813826"
        user_2.firmnumber = "848135"
        user_2.accountnumber = "30413594"
        user_2.companyname = "MIRABELLA FINANCIAL"
        user_2.emailaddress = "SEANSYSTEM2@Bloomberg.net"
        user_2.corporateemailaddress = "sean@system2capital.com"
        user_2.domain = "system2capital.com"

        user_list = msgToGroup()
        user_list.add_user(user)
        user_list.add_user(user_1)
        user_list.add_user(user_2)

        response = user_list.userList
        print(response)

    # test_msgToList()
