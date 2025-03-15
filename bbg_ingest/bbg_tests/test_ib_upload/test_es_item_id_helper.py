from bbg_helpers.es_bbg_ib_index import BBG_IB
from bbg_helpers.es_bbg_ib_index import item_id as ItemID
from bbg_src.ib_upload_lambda.bbg_ib_conversation.es_item_id_helper import (
    _conversation_id_part,
    generate_item_id,
)


class TestFunction:
    def test_conversation_id_part(self):
        CASES = [
            ("PCHAT-0x10000027EB748", "0x10000027EB748"),
            ("CHAT-fs:6017C5E3192C0029", "6017C5E3192C0029"),
        ]
        for input, expected in CASES:
            result = _conversation_id_part(conversation_id=input)
            assert result == expected

    def test_generate_item_id(self):
        bbg_record: BBG_IB = BBG_IB()
        bbg_record.conversationid = "PCHAT-0x10000027EB748"
        bbg_record.datetimeutc = "1612249838"

        expected_item_id: ItemID = ItemID()
        expected_item_id.es_id = "0x10000027EB74821020286"
        expected_item_id.item_date = "210202"
        expected_item_id.item_id = "0x10000027EB748"
        expected_item_id.item_number = "86"

        result = generate_item_id(ibMessage=bbg_record, messageNumber=86)
        assert result == expected_item_id
