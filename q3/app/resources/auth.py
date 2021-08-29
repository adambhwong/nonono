import json, falcon, logging, cgi, conf
from modules.tslcApi import IdentityAccessManager

LOG_CFG=conf.LOG_CFG

# configure logger
logging.basicConfig(level=LOG_CFG["level"],datefmt=LOG_CFG["datefmt"],format=LOG_CFG["format"])

class GetPublicKeyResource:

    def on_get(self, req, resp):
        iam = IdentityAccessManager()
        key = iam.getPublicKey()
        logging.info('pub_key: \n{}\n'.format(key))
        body = json.dumps({'publicKey': key})
        resp.status = falcon.HTTP_200
        resp.text = body

class GetTokenResources:

    def on_post(self, req, resp):
        data = json.loads(req.stream.read().decode('utf-8'))
        try:
            usr=data['username']
            pwd=data['password']
        except:
            raise falcon.HTTPBadRequest(
                "Invalid post JSON",
                "Missing 'username' or 'password' in request JSON."
            )
        iam = IdentityAccessManager()
        result = iam.authenticate(usr, pwd)
        if not result['success']:
            raise falcon.HTTPUnauthorized(
                description=result['msg']
            )
        token = iam.genToken(result)
        body = json.dumps({'token': token})
        resp.status = falcon.HTTP_200
        resp.text = body
