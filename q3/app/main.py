import falcon, conf
import resources.shortenUrl as surl

#ALLOW_ORGS=conf.ALLOW_ORGS
BASE_PATH=''

app = falcon.App()
#app = falcon.App(middleware=falcon.CORSMiddleware(allow_origins=ALLOW_ORGS, allow_credentials='*'))
app.add_route(BASE_PATH + '/newurl', surl.NewUrlResources())
app.add_route(BASE_PATH + '/{sUrl}', surl.GetOriginalUrlResources())
