import unittest

import os
import boto3
from dotenv import load_dotenv
from dynamo import DynamoClient

load_dotenv() 


dynamo_client = DynamoClient(region_name=os.environ.get('REGION_NAME'),aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'), aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'))
TABLE_NAME = "Categories"
TABLE_NAMES = ['Table1','Table2','Table3']
KeySchema=[
    {
        'AttributeName': 'Pk',
        'KeyType': 'HASH' 
    },
]
AttributeDefinitions=[
    {
        'AttributeName': 'Pk',
        'AttributeType': 'S'
    },        
]


class TestDynamoClient(unittest.TestCase):
       
    def test_create_tables(self):
        
        for table_name in TABLE_NAMES:
            try:
                dynamo_client.create_table(table_name,key_schema=KeySchema,attribute_definition=AttributeDefinitions)                        
            except Exception as ex:
                print(ex)
            table_info = dynamo_client.get_table_information(table_name=table_name)
            self.assertIsNotNone(table_info,f"Table {table_name} found")
        
    def test_put_item(self):
        items = [
            {
                'Pk':{'S':'C1'},
                'name':{'S':'Toys'},
                'price':{'S':'150'},
                'origin':{'S':'Costa Rica'}
            },
            {
                'Pk':{'S':'C2'},
                'name':{'S':'Fruits'},
                'price':{'S':'250'},
                'origin':{'S':'Costa Rica'}
            },
            {
                'Pk':{'S':'C3'},
                'name':{'S':'Healt products'},
                'price':{'S':'4250'},
                'origin':{'S':'Costa Rica'}
            },
            {
                'Pk':{'S':'C4'},
                'name':{'S':'Tools'},
                'price':{'S':'8450'},
                'origin':{'S':'Costa Rica'}
            }
        ]
                
        for item in items:
            dynamo_client.put_item(TABLE_NAME,item=item)

        count_items = 0
        for item in dynamo_client.get_all_item(TableName="Categories",total_segments=25, max_scan_in_parallel=4):    
            count_items+=1
                
        self.assertEqual(len(items),count_items,'Not all items was created')

    def test_update_item(self):
        key = {'Pk':{'S':'C1'}}
        update_expression='set price =:p'
        expression_attribute_values={":p":{"S":"888"}}
        dynamo_client.updated_item('Categories',key,update_expression,expression_attribute_values)
        item = dynamo_client.get_item(TABLE_NAME,key=key)
        self.assertEqual(item.get('price'),expression_attribute_values.get(':p'),"The Price is different")

    def test_delete_item(self):
        key = {'Pk':{'S':'C1'}}
        dynamo_client.delete_item(TABLE_NAME,key=key)        
        
    def test_delete_table(self):
        for table_name in TABLE_NAMES:
            dynamo_client.delete_table(table_name=table_name)
            table_info = dynamo_client.get_table_information(table_name=table_name)
            self.assertIsNotNone(table_info,f"Table {table_name} not was deleted")
                
        
if __name__ =='__main__':
    unittest.main()