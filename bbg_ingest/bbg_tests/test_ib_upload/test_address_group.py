from bbg_helpers.es_bbg_ib_index import bloomberg_id
from bbg_src.ib_upload_lambda.bbg_ib_conversation.process_single_conversation import (
    msgToGroup,
)

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
user_2.uuid = "25813826"
user_2.firmnumber = "848135"
user_2.accountnumber = "30413594"
user_2.companyname = "MIRABELLA FINANCIAL"
user_2.emailaddress = "SEANSYSTEM2@Bloomberg.net"
user_2.corporateemailaddress = "sean@system2capital.com"
user_2.domain = "system2capital.com"


class TestFunctions:
    def test_user_list_remove_from_empty_list(self):
        user_list = msgToGroup()

        # Check that removing a user from an empty list doesn't break stuff
        user_list.remove_user(user)
        response = user_list.userList
        assert len(response) == 0

    def test_add_same_user_twice(self):
        user_list = msgToGroup()

        user_list.add_user(user)
        user_list.add_user(user)
        response = user_list.userList
        assert len(response) == 1
        assert response[0] == user

    def test_add_and_remove_user(self):
        user_list = msgToGroup()

        user_list.add_user(user)
        user_list.add_user(user_1)
        user_list.remove_user(user_1)

        response = user_list.userList
        assert len(response) == 1
        assert response[0] == user

    def test_get_to_list(self):
        user_list = msgToGroup()
        user_list.add_user(user)
        user_list.add_user(user_1)
        user_list.add_user(user_2)
        response = user_list.get_to_list(messageFrom=user_2)

        assert len(response) == 2
        assert user in response
        assert user_1 in response
        assert user_2 not in response
