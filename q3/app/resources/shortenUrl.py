import json, falcon, logging, cgi, conf
from modules.shortenUrlApi import UrlShortener

LOG_CFG=conf.LOG_CFG

# configure logger
logging.basicConfig(level=LOG_CFG["level"],datefmt=LOG_CFG["datefmt"],format=LOG_CFG["format"])

class GetOriginalUrlResources:

    def on_get(self, req, resp, sUrl):
        oUrl = UrlShortener().getOriginalUrl(sUrl)
        if not oUrl:
            resp.status = falcon.HTTP_404
        else:
            resp.append_header("content-location", oUrl)
            resp.status = falcon.HTTP_304

class NewUrlResources:

    def on_post(self, req, resp):
        data = json.loads(req.stream.read().decode('utf-8'))
        logging.debug(json.dumps(data))
        oUrl = data["url"]
        sUrl = UrlShortener().addUrl(oUrl)
        if sUrl:
            respJson = { "url": oUrl, "shortenUrl": req.url.replace("newurl", sUrl) }
            resp.status = falcon.HTTP_200
            resp.text = json.dumps(respJson, indent=4)
        else:
            resp.status = falcon.HTTP_409
