import os
import pprint
from typing import List
import boto3
import json
import logging
import time
import decimal
import concurrent.futures
import itertools

from botocore.exceptions import BotoCoreError, ClientError, ParamValidationError
from boto3.dynamodb.conditions import Key


logger = logging.getLogger()

class DynamoClient():
    def __init__(self, region_name:str, aws_access_key_id:str, aws_secret_access_key:str):
        self.region_name = region_name
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key        
        self.dynamo_client = boto3.client('dynamodb', region_name=region_name,aws_access_key_id=self.aws_access_key_id,aws_secret_access_key=self.aws_secret_access_key)
        self.table = None
        self.table_information = None
        self.tables = []
    
    def get_client(self):
        
        self.dynamo_client  =  boto3.client(service_name = 'dynamodb',region_name = self.region_name,
            aws_access_key_id = self.aws_access_key_id,
            aws_secret_access_key = self.aws_secret_access_key)
        
        return self.dynamo_client
    
    
    def create_table(self,table_name:str, key_schema:dict,attribute_definition:dict, read_capacity_units:int=10, write_capacity_units:int=10)->dict:                           
        """
            Create a dynamo_client table.
            :param table_name: The name of the table to check.
            :param key_schema: The dict with key schemas to create the table.
            :param attribute_definition: The dict with attributes definition to create the table.
            :param read_capacity_units: A read capacity unit represents one strongly consistent read per second, or two eventually consistent reads per second, for an item up to 4 KB in size, 
                                        For example, suppose that you create a table with 10 provisioned read capacity units. This allows you to perform 10 strongly consistent reads per second, or 20 eventually consistent reads per second, for items up to 4 KB.
                                        Reading an item larger than 4 KB consumes more read capacity units. For example, a strongly consistent read of an item that is 8 KB (4 KB × 2) consumes 2 read capacity units. An eventually consistent read on that same item consumes only 1 read capacity unit.
                                        The default value is 10.
            :param write_capacity_units: A write capacity unit represents one write per second, for an item up to 1 KB in size.
                                        For example, suppose that you create a table with 10 write capacity units. This allows you to perform 10 writes per second, for items up to 1 KB in size per second.
                                        Item sizes for writes are rounded up to the next 1 KB multiple. For example, writing a 500-byte item consumes the same throughput as writing a 1 KB item.
                                        The default value is 10.                    
        """
        try:
            self.table = self.dynamo_client.create_table(
                TableName=table_name,
                KeySchema=key_schema,
                AttributeDefinitions=attribute_definition,
                ProvisionedThroughput={
                    'ReadCapacityUnits': read_capacity_units,
                    'WriteCapacityUnits': write_capacity_units
                }
            )                        
            logger.info(f"Table {table_name} successfully created")

        except ClientError as err:
            error_msg = f"Couldn't create table {table_name}. Here's why: {err.response['Error']['Code']}:{err.response['Error']['Message']}"
            logger.debug(error_msg)
            logger.error(error_msg)
        
            raise
        return self.table
    
    
    def list_tables(self)->List:
        """
        Lists the Amazon dynamo_client tables for the current account.

        :return: The list of string with the names of the tables.
        """
        try:
            return self.dynamo_client.list_tables()['TableNames']        
        
        except ClientError as err:
            logger.debug(f"Couldn't list tables. Here's why: {err.response['Error']['Code']}: {err.response['Error']['Message']}")                
            raise
        
    def delete_table(self,table_name:str)->bool:
        """
        Delete a table if exists.

        :param table_name: The name of the table to check.
        :return: boolean True if deleted and false in error case
        
        """
        deleted = False
        try:
            self.dynamo_client.delete_table(TableName=table_name)
            logger.info(f"Table {table_name} was successfully deleted")  
            deleted = True
        except Exception as err:
            logger.debug(f"Error trying delete the table {table_name} \n {err}")  
        return deleted
        
        
    def get_table_information(self, table_name:str)->bool:
        """
        Determines whether a table exists. As a side effect, stores the table in
        a member variable.

        :param table_name: The name of the table to check.
        :return: True when the table exists; otherwise, False.
        """
        exists = False
        
        try:
            self.table_information = self.dynamo_client.describe_table(TableName=table_name)
            exists = True
        except ClientError as err:
            if err.response['Error']['Code'] == 'ResourceNotFoundException':
                logger.debug(f"Error getting information of {table_name}. Here's why: {err.response['Error']['Code']}: {err.response['Error']['Message']}")                
            else:
                logger.debug(f"Couldn't check for existence of {table_name}. Here's why: {err.response['Error']['Code']}: {err.response['Error']['Message']}")
                raise
        return exists
    

    def table_query(self, table_name,key_condition_expression:str, expression_attribute_values:dict, scan_index_forward:bool=False,limit:int=1)->dict:
        """
        Get item data.

        :param table_name: The name of the table to check.
        :param key_condition_expression: Determines what we’re looking for. EXample: "Pk = :id"
        :param expression_attribute_values:  Specify a variable stored in this dict. Example: {":id":{"S":"C1"}}
        :param scan_index_forward: Specifies the order for index traversal: If true (default), 
            the traversal is performed in ascending order; if false , the traversal is performed in descending order. 
            Items with the same partition key value are stored in sorted order by sort key.
        :param limit: A single Query operation can retrieve a maximum of 1 MB of data. 
            This limit applies before any FilterExpression or ProjectionExpression is applied to the results. 
            If LastEvaluatedKey is present in the response and is non-null, you must paginate the result set
        """
        
        if key_condition_expression and expression_attribute_values:
            try:                
                response = self.dynamo_client.query(
                    TableName = table_name,
                    KeyConditionExpression=key_condition_expression,
                    ExpressionAttributeValues=expression_attribute_values,                    
                    ScanIndexForward=scan_index_forward,
                    Limit=limit
                    
                )
                
            except ClientError as err:
                if err.response['Error']['Code'] == 'ResourceNotFoundException':
                    logger.debug(f"Error executing the query. Here's why: {err.response['Error']['Code']}: {err.response['Error']['Message']}")                
                else:
                    logger.debug(f"Couldn't check for existence of {table_name}. Here's why: {err.response['Error']['Code']}: {err.response['Error']['Message']}")
                    raise
                
            else:
                return response['Items']
        else:
            logger.debug("Key condition expression and expression attribute values are required")
            return None
    
    
    def put_item(self, table_name:str,item:dict)->bool:                
        """
        Store the item into the a table specific in the table_name parameter.

        :param table_name: The name of the table to check.
        :param item: information to storage into the table.
        :return: True when the table exists; otherwise, False.
        """
        success = False
        try:           
            self.dynamo_client.put_item(TableName=table_name, Item=item)
            success = True
        except ClientError as err:
            if err.response['Error']['Code'] == 'ResourceNotFoundException':
                logger.debug(f"Error putting item in {table_name}. Here's why: {err.response['Error']['Code']}: {err.response['Error']['Message']}")                
            else:
                logger.debug(f"Couldn't check for existence of {table_name}. Here's why: {err.response['Error']['Code']}: {err.response['Error']['Message']}")
                raise
        
        except Exception as err:            
            logger.debug(f"Couldn't put the item into the table {table_name}. Here's why: {err.response['Error']['Code']}: {err.response['Error']['Message']}")            
            
        return success


    def get_item(self, table_name:str,key:dict):
        """
        Get item data.

        :param table_name: The name of the table to check.
        :param key: key for get item data storage into the table.
        :return: Dict with the information or None in case of error.
        """
        
        try:
            result = self.dynamo_client.get_item(TableName=table_name,
                                 Key=key)            
        
            logger.info(f"Get item result {result.get('Item')}")            
            return result.get('Item')
        
        except Exception as err:
            logger.debug(f"Couldn't get item from the table {table_name}. Here's why: {err.response['Error']['Code']}: {err.response['Error']['Message']}")                        
            return None            
                       
                                

    def updated_item(self,table_name:str,key:dict,update_expression:str, expression_attribute_values:dict):
        """
            Update item info using the updated_expression and the expression_attribute_values parameter.

            :param table_name: The name of the table to check.
            :param key: key for get item data storage into the table. Example: key = {'Pk':{'S':'C1'}}
            :param update_expression: set the field and the variable to update. Example: update_expression='set price =:p'
            :param expression_attribute_values: assignee the value to update at the variable. Example: expression_attribute_values={":p":{"S":"888"}}
        
        """

        try:
            result = self.dynamo_client.update_item(
                            TableName=table_name,
                            Key=key,
                            UpdateExpression=update_expression,
                            ExpressionAttributeValues=expression_attribute_values,
                            ReturnValues="UPDATED_NEW"
                            )            
        
            return result
        
        except Exception as err:
            logger.debug(f"Couldn't update an item in the table {table_name}. Here's why: {err}")                        
            print(f"Couldn't update an item in the table {table_name}. Here's why: {err}")                        
            return None            


    def delete_item(self,table_name:str,key:dict):
        """
            Update item info using the updated_expression and the expression_attribute_values parameter.

            :param table_name: The name of the table to check.
            :param key: key to get the item stored in the table, which will be deleted. Example: key = {'Pk':{'S':'C1'}}        
        """

        try:
            result = self.dynamo_client.delete_item(TableName=table_name,Key=key)            

        
        except Exception as err:
            logger.debug(f"Couldn't delete the item in the table {table_name}. Here's why: {err}")                        
            print(f"Couldn't delete the item in the table {table_name}. Here's why: {err}")                        
            result = None            
        return result

    def get_all_item(self, *, TableName, total_segments=25, max_scan_in_parallel=5, **kwargs):
        """
        Generates all the items in a DynamoDB table.
        This does a Parallel Scan operation over the table.

        :param TableName: The name of the table to scan.
        :param total_segments: How many segments to divide the table into?  As long as this is >= to the
            number of threads used by the ThreadPoolExecutor, the exact number doesn't
            seem to matter.        
        :param max_scan_in_parallel: How many scans to run in parallel?  If you set this really high you could
            overwhelm the table read capacity, but otherwise I don't change this much.
                

        """
        total_segments = total_segments
        max_scans_in_parallel = max_scan_in_parallel

        # Schedule an initial scan for each segment of the table.  We read each
        # segment in a separate thread, then look to see if there are more rows to
        # read -- and if so, we schedule another scan.
        tasks_to_do = [
            {
                **kwargs,
                "TableName": TableName,
                "Segment": segment,
                "TotalSegments": total_segments,
            }
            for segment in range(total_segments)
        ]

        # Make the list an iterator, so the same tasks don't get run repeatedly.
        scans_to_run = iter(tasks_to_do)

        with concurrent.futures.ThreadPoolExecutor() as executor:

            # Schedule the initial batch of futures.  Here we assume that
            # max_scans_in_parallel < total_segments, so there's no risk that
            # the queue will throw an Empty exception.
            futures = {
                executor.submit(self.dynamo_client.scan, **scan_params): scan_params
                for scan_params in itertools.islice(scans_to_run, max_scans_in_parallel)
            }

            while futures:
                # Wait for the first future to complete.
                done, _ = concurrent.futures.wait(
                    futures, return_when=concurrent.futures.FIRST_COMPLETED
                )

                for fut in done:
                    yield from fut.result()["Items"]

                    scan_params = futures.pop(fut)

                    # A Scan reads up to N items, and tells you where it got to in
                    # the LastEvaluatedKey.  You pass this key to the next Scan operation,
                    # and it continues where it left off.
                    try:
                        scan_params["ExclusiveStartKey"] = fut.result()["LastEvaluatedKey"]
                    except KeyError:
                        break
                    tasks_to_do.append(scan_params)

                # Schedule the next batch of futures.  At some point we might run out
                # of entries in the queue if we've finished scanning the table, so
                # we need to spot that and not throw.
                for scan_params in itertools.islice(scans_to_run, len(done)):
                    futures[executor.submit(self.dynamo_client.scan, **scan_params)] = scan_params


    def get_batch_items(self,batch_keys)->dict:
        """
        Gets a batch of items from Amazon DynamoDB. Batches can contain keys from
        more than one table.

        When Amazon DynamoDB cannot process all items in a batch, a set of unprocessed
        keys is returned. This function uses an exponential backoff algorithm to retry
        getting the unprocessed keys until all are retrieved or the specified
        number of tries is reached.

        :param batch_keys: The set of keys to retrieve. A batch can contain at most 100
                        keys. Otherwise, Amazon DynamoDB returns an error.
        :return: The dictionary of retrieved items grouped under their respective
                table names.
        """

        tries = 0
        max_tries = 5
        sleepy_time = 1  # Start with 1 second of sleep, then exponentially increase.
        
        retrieved = {key: [] for key in batch_keys}
        while tries < max_tries:
            response = self.dynamo_client.batch_get_item(RequestItems=batch_keys)
            # Collect any retrieved items and retry unprocessed keys.
            for key in response.get('Responses', []):
                retrieved[key] += response['Responses'][key]
            unprocessed = response['UnprocessedKeys']
            if len(unprocessed) > 0:
                batch_keys = unprocessed
                unprocessed_count = sum(
                    [len(batch_key['Keys']) for batch_key in batch_keys.values()])
                logger.info(
                    "%s unprocessed keys returned. Sleep, then retry.",
                    unprocessed_count)
                tries += 1
                if tries < max_tries:
                    logger.info("Sleeping for %s seconds.", sleepy_time)
                    time.sleep(sleepy_time)
                    sleepy_time = min(sleepy_time * 2, 32)
            else:
                break

        return retrieved
