from django.test import TestCase                
from django.test.client import Client
from django.conf import settings

settings.DEBUG = True

class dashboard(TestCase):
    fixtures = ["auth.json", "base.json", "observations.json", "zones.json"]
        
    def testPasses(self):
        clt = Client()
        res = clt.get("/")
        assert res.status_code == 302
        # admin is a superuser
        clt.login(username='admin', password='admin')
        res = clt.get("/")
        assert res.status_code == 200
        res = clt.get("/zone/1/") # North Region
        assert res.status_code == 200
        res = clt.get("/district/")
        assert res.status_code == 200
        res = clt.get("/facility/7/") # North Region > Karonga > Kaporo
        assert res.status_code == 200
        res = clt.get("/zone/5/") # North Region > Karonga
        assert res.status_code == 200
        res = clt.get("/gmc/")
        assert res.status_code == 200

