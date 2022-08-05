from helloasso_api import HaApiV5

class OrganizationApi(object):
    def __init__(self, client):
        self._client = client

    def get_by_slug(self, slug: str) -> dict:
        return self._client.call(f"organizations/{slug}").json()

class MyApi(HaApiV5):
    def __init__(self, *args, **kwargs):
        super(MyApi, self).__init__(*args, **kwargs)
        self.organization = OrganizationApi(self)

api_permacat = MyApi(
        api_base='api.helloasso.com',
        client_id='XXXXXXXXXXX',
        client_secret='XXXXXXXX',
        timeout=60
)

def initAPI():
    api_permacat.authorization.generate_authorize_request(redirect_url=)
    api_permacat.organization.get_by_slug("XXXXXXXXX")