import helpers.es_slack_id
import pytest


def test_get_user_info():
    user = helpers.es_slack_id.get_user_info_from_slack("NONSENSE", "ips")
    assert user is None

    user = helpers.es_slack_id.get_user_info_from_slack("UP2JNQM9R", "ips")
    print(user)
    assert user["name"] == "tom"
    assert user["profile"]["real_name"] == "Tom Vavrechka"


def test_get_user_info_no_param():
    user = helpers.es_slack_id.get_user_info_from_slack("NONSENSE", "madeupclient")
    assert user is None


def test_from_inner_doc_creator():
    siidc = helpers.es_slack_id.SlackIdInnerDocCreator("ips", {}, {})
    i_d = siidc.get_slack_id_inner_doc("UP2JNQM9R")
    from pprint import pprint

    print("i_d")
    pprint(i_d)
    print(type(i_d))
    assert i_d.fullname == "Tom Vavrechka"
    assert i_d.firstname == "Tom"


def test_from_inner_doc_creator_fail():
    # Test to see that no client supplied causes error
    siidc = helpers.es_slack_id.SlackIdInnerDocCreator("", {}, {})
    with pytest.raises(Exception) as e_info:
        _ = siidc.get_slack_id_inner_doc("UP2JNQM9R")
    assert "Client name should not be blank" in str(e_info.value)


def test_from_inner_doc_creator_fail_2():
    # Test to see that final else clause is reached if no such user
    siidc = helpers.es_slack_id.SlackIdInnerDocCreator("ips", {}, {})
    i_d = siidc.get_slack_id_inner_doc("NONSENSE")
    assert i_d.slackid == "NONSENSE"
    assert i_d.fullname == "NONSENSE"
