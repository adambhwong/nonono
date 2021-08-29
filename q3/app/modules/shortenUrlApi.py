import logging, re, json, uuid, boto3, conf
from time import time
from datetime import datetime, timedelta
from boto3.dynamodb.conditions import Key

LOG_CFG=conf.LOG_CFG
DYNDB_TBL=conf.DYNDB_TBL

# configure logger
logging.basicConfig(level=LOG_CFG["level"],datefmt=LOG_CFG["datefmt"],format=LOG_CFG["format"])

class UrlShortener:
    def __init__(self, tableCfg=DYNDB_TBL):
        self.tblName = tableCfg["name"]
        self.sUrlKey = tableCfg["sUrlKey"]
        self.oUrlKey = tableCfg["oUrlKey"]
        self.oUrlIdx = tableCfg["oUrlIdx"]
        self.table = boto3.resource('dynamodb').Table(tableCfg["name"])
   
    def getShortenUrl(self, url):
        response = self.table.query(
            IndexName = self.oUrlIdx,
            KeyConditionExpression=Key(self.oUrlKey).eq(url)
        )
        logging.debug(json.dumps(response))
        if response['Count'] == 0:
            return None
        return response['Items'][0][self.sUrlKey]
        
    def getOriginalUrl(self, url):
        response = self.table.query(
            KeyConditionExpression=Key(self.sUrlKey).eq(url)
        )    
        logging.debug(json.dumps(response))
        if response['Count'] == 0:
            return None
        return response['Items'][0][self.oUrlKey]
        
    def addUrl(self, url):
        oUrl = url
        if self.getShortenUrl(url):
            return None
        sUrl = uuid.uuid5(uuid.NAMESPACE_URL, url).hex[:8]
        logging.debug(json.dumps(sUrl))
        response = self.table.update_item(
            Key = {
                self.sUrlKey: sUrl,
                self.oUrlKey: oUrl
            }
        )
        logging.debug(json.dumps(response))
        if response["ResponseMetadata"]["HTTPStatusCode"] != 200:
            return None
        return sUrl
