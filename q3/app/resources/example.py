import json, falcon, logging, cgi, conf

LOG_CFG=conf.LOG_CFG

# configure logger
logging.basicConfig(level=LOG_CFG["level"],datefmt=LOG_CFG["datefmt"],format=LOG_CFG["format"])

class HelloWorldResource:

    def on_get(self, req, resp):

        resp.media = ('Hello World from Falcon Python 3.6 app with' +
                          ' Gunicorn running in a container.')
class GetPostDataResource:

    def on_post(self, req, resp):
        data = json.loads(req.stream.read().decode('utf-8'))
        logging.info(json.dumps(data))
        body = json.dumps(data)
        resp.status = falcon.HTTP_200
        resp.body = body

class GetPostFileResource:

    def on_post(self, req, resp):
        logging.info("post request contnet-type: {0}".format(req.content_type))
        if req.content_type is not None:
            if req.content_type.find('multipart/form-data') == 0:
                upload = cgi.FieldStorage(fp=req.stream, environ=req.env)
                for part in upload:
                    if upload[part].filename:
                       logging.info("filename: {0}".format(upload[part].filename))
                       data = upload[part].file.read()
                       body = data
            else:
                body = req.stream.read()
        else:
            body = req.stream.read()
        resp.status = falcon.HTTP_200
        resp.body = body
