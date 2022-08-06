from helloasso_api import HaApiV5
import requests
import simplejson

from .pcat_infos import ID_PCAT

pcat_slug = "permaculture-catalane"

class OrganizationApi(object):
    def __init__(self, client):
        self._client = client

    def get_by_slug(self, slug: str) -> dict:
        return self._client.call(f"/V5/organizations/{slug}").json()

class MyApi(HaApiV5):
    def __init__(self, *args, **kwargs):
        super(MyApi, self).__init__(*args, **kwargs)
        self.organization = OrganizationApi(self)



def initAPI(request):
    api_permacat = MyApi(
        api_base='api.helloasso.com',
        client_id=ID_PCAT["client_id"],
        client_secret=ID_PCAT["client_secret"],
        timeout=60,
    )
    def initAPI_old(request):
        x = api_permacat.authorization.generate_authorize_request(redirect_url="http://127.0.0.1:8000/HA/api/success")
        y = api_permacat.organization.get_by_slug(pcat_slug)
        print(y)
    def getrefreshToken():
        url = "https://api.helloasso.com/oauth2/token"
        headers = {"Content-Type":"application/x-www-form-urlencoded"}
        payload = {"grant_type":"client_credentials", "client_id":api_permacat.client_id, "client_secret":api_permacat.client_secret}
        reponse = requests.post(url, data=payload, headers=headers)
        data = simplejson.loads(reponse.text)
        print(data)
    #refreshToken = getrefreshToken()
    refreshToken = {"access_token":"eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiJjMmY1OGY5MDgyOGI0YjQxOWExMTcyYjE4OTVlZTIwNCIsImNwcyI6WyJBY2Nlc3NQdWJsaWNEYXRhIiwiQWNjZXNzVHJhbnNhY3Rpb25zIiwiQ2hlY2tvdXQiXSwidXJzIjoiT3JnYW5pemF0aW9uQWRtaW4iLCJuYmYiOjE2NTk4MDEwMzIsImV4cCI6MTY1OTgwMjgzMiwiaXNzIjoiaHR0cHM6Ly9hcGkuaGVsbG9hc3NvLmNvbSIsImF1ZCI6IjhjNTYyZWZlMmQzYzRhZDZhNTFlOTNmMzE5ZGM3MmE1In0.VCJyl8oGQwWCGjrJ7RBSmZNqnLGQpvuVcGR_tHuFKyY_aNX80oH3SuM_8a8mDsfNgdBafIQw2XvK_9KpQ1xWU_AjYLLdIq9i_PR1nSatXJJbRKZpYkGkL1Om1g-4xde6NxQ4pVyZ2l8EFtbbn-_adWPgd9kbQ5X4Om3M9sxzonuPuRYpOIEemHZ-6FmXtrsM06BgSmKAQb6HGV9gW__XHC4SFutSp9BVMT4-TKTGOvB27L4TEoDC8ALufrmlYBdsqh61QEFYe31HgL4LrLzm3nqORKn45LoNKTX3Y_eSU0wQup2NBbZtHdE2Dw4zzODbmUBqtkFvPRaNWZ10pjVuIQ","token_type":"bearer","expires_in":1799,"refresh_token":"OOnwH38TmPTrtaHjIhAxKUJMDY476vsItbVe7NN5xInC6da5PgQ-2fssTLTQVXsly3uoo8J7KqZNJYSjZaQf2egsE-KYlf2Er8Bk3tdUSpccQ8IHZSJ6JMR19rJS9MHdgN0Ux0-SV7Z6hkmQtlSoLTNyezEV3pjKvm-LvY2hvYqEyU8DyMtbm9LlwSuey3WqlKx9bjvmC12w5pqGyeFb5jK6WWxsWCJMhlWddvokJHuhw7yoie58qwf23DnK-shyKNX_UadYyaIMB-yysQYC6eK9draKDwFTxTMQkZ94QS2rzoSQMGZnPeHT0y63ZNSi1oeeHfVcUr4RoC99PFcn8YMR4R5fpCg7HvjnzgksyduqoXqRvupX-W_os1OFZqzYTOHrY5GRP1pm8fwSCBdTMuEStW0"}

    def getDataAsso():
        url = "https://api.helloasso.com/v5/organizations/" + pcat_slug
        headers = {"authorization": "Bearer "+ refreshToken["access_token"]}
        reponse = requests.get(url, headers=headers)
        data = simplejson.loads(reponse.text)
        print(data)

    #data_asso = getDataAsso()
    data_asso = {'isAuthenticated': True, 'fiscalReceiptEligibility': False, 'fiscalReceiptIssuanceEnabled': False, 'type': 'Association1901', 'category': 'Environnement', 'name': 'PERMAculture CATalane', 'role': 'OrganizationAdmin', 'city': 'Perpignan', 'zipCode': '66000', 'description': "Réseau d'échanges et d'entraide visant à promouvoir les valeurs et outils de la permaculture", 'url': 'https://www.helloasso.com/associations/permaculture-catalane', 'organizationSlug': 'permaculture-catalane'}

    def getAccessToken():
        url = "https://api.helloasso.com/oauth2/token"
        headers = {"Content-Type":"application/x-www-form-urlencoded"}
        payload = {"grant_type":"refresh_token", "client_id":api_permacat.client_id, "refresh_token":refreshToken["refresh_token"]}
        reponse = requests.post(url, data=payload, headers=headers)
        data = simplejson.loads(reponse.text)
        print(data)
    #accessToken = getAccessToken()
    accessStoken = {'access_token': 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiJjMmY1OGY5MDgyOGI0YjQxOWExMTcyYjE4OTVlZTIwNCIsImNwcyI6WyJBY2Nlc3NQdWJsaWNEYXRhIiwiQWNjZXNzVHJhbnNhY3Rpb25zIiwiQ2hlY2tvdXQiXSwidXJzIjoiT3JnYW5pemF0aW9uQWRtaW4iLCJuYmYiOjE2NTk4MDI2MDAsImV4cCI6MTY1OTgwNDQwMCwiaXNzIjoiaHR0cHM6Ly9hcGkuaGVsbG9hc3NvLmNvbSIsImF1ZCI6IjhjNTYyZWZlMmQzYzRhZDZhNTFlOTNmMzE5ZGM3MmE1In0.LR4IcEVKwCj9pkEEvKNemgF4-AjtiEY0l8zwyxBEO7AeiiGQdYJjyLN8601yRiQIQR0c2kV_6QteCUbnVEj189ygSU8rvetbP65XdyKACigQ3oEHao5brr1UkOAP2nFZO6z-YPA5MYs1UtrVdd5uA_W8V8FCBsj1cXuQ-u7mLfhdzQalKuuCdOCabnJmIwLtgqDdfLW5L4dEXduwDLrPQANS0uu1THdF0_Fu2qDVfmnhkGC82GoIi0FcgTK3DVwyAM8zv7QHdNdDx6Y_xcmzj1vej5jNAkgfyPNiajHjyLcY8loUHNzCiAl_WhjKerY8PGVU24w-ZVHxRQT-H0ivHg', 'token_type': 'bearer', 'expires_in': 1799, 'refresh_token': 'criA970_soh5jiFlXC_X9L6Lz_mYBhOin3WIP_qYw7E5-8SDduig7TeqL9385-XVwOWna8mo9H_c37xcRuSk_5M02ZNcKdxzor5OidmnwZsuIwHJzfQujCmqhC0GndRL6kKh-lXAJLQ1_M5utiMaaSpb-qiIt31n5GA9iIIXpy2mufCnaZh-CfXf1EIr4dnBskpPGpRezPOHwuKq4rf4NnhxOubweCinCXl5Gqvbrsz_uk16UHfNbixWcxoUFRZQjSh0Vm6Dh1Rsw5QxHoeb8jWje6mEfFEASRSNRh57K39W2Sq7DPMoF_E55Bz8ijY8Q0du9x86-0dO0ON1OceMOJXAL9-4HqJBKqxML5iWLzXKIDVkKfpBIqOz6aFAV-mVIIRerzeX5y_4SNwpbsOydit9xKw'}

    def getFormTypes():
        url = "https://api.helloasso.com/v5/organizations/" + pcat_slug + "/formTypes"
        headers = {"authorization": "Bearer "+ accessStoken["access_token"]}
        reponse = requests.get(url, headers=headers)
        data = simplejson.loads(reponse.text)
        print(data)

    #formTypes = getFormTypes()
    formTypes = ['Checkout', 'Donation', 'CrowdFunding', 'Membership']

    def getForms(type):
        url = "https://api.helloasso.com/v5/organizations/" + pcat_slug + "/forms/"
        headers = {"authorization": "Bearer "+ accessStoken["access_token"]}
        reponse = requests.get(url, headers=headers)
        data = simplejson.loads(reponse.text)
        print(data)

    #forms = getForms(formTypes[3])
    forms = {'data': [{'currency': 'EUR', 'description': "Mettre en place plusieurs ruches pour la sauvegarde de l'abeille", 'endDate': '2022-06-01T00:00:00+02:00', 'logo': {'fileName': 'pexels-alexas-fotos-2198671 1 -8223f63457b049a0b19f96dbac558b53.jpg?bb=3x152x900x450&sb=900x681', 'publicUrl': 'https://cdn.helloasso.com/img/photos/collectes/pexels-alexas-fotos-2198671 1 -8223f63457b049a0b19f96dbac558b53.jpg?bb=3x152x900x450&sb=900x681'}, 'meta': {'createdAt': '2022-04-04T21:41:30.007+02:00', 'updatedAt': '2022-07-11T13:41:01.5+02:00'}, 'state': 'Public', 'title': 'Projet Bzzzz', 'widgetButtonUrl': 'https://www.helloasso.com/associations/permaculture-catalane/collectes/projet-bzzzz/widget-bouton', 'widgetFullUrl': 'https://www.helloasso.com/associations/permaculture-catalane/collectes/projet-bzzzz/widget', 'widgetVignetteHorizontalUrl': 'https://www.helloasso.com/associations/permaculture-catalane/collectes/projet-bzzzz/widget-vignette-horizontale', 'widgetVignetteVerticalUrl': 'https://www.helloasso.com/associations/permaculture-catalane/collectes/projet-bzzzz/widget-vignette', 'formSlug': 'projet-bzzzz', 'formType': 'CrowdFunding', 'url': 'https://www.helloasso.com/associations/permaculture-catalane/collectes/projet-bzzzz', 'organizationSlug': 'permaculture-catalane'}, {'currency': 'EUR', 'startDate': '2022-01-01T00:00:00+00:00', 'endDate': '2023-01-31T23:59:59.999+00:00', 'meta': {'createdAt': '2022-01-11T11:11:10.857+01:00', 'updatedAt': '2022-01-11T21:38:33.907+01:00'}, 'state': 'Public', 'title': "Adhésion à l'association 2022", 'widgetButtonUrl': 'https://www.helloasso.com/associations/permaculture-catalane/adhesions/adhesion-a-l-association-2/widget-bouton', 'widgetFullUrl': 'https://www.helloasso.com/associations/permaculture-catalane/adhesions/adhesion-a-l-association-2/widget', 'widgetVignetteHorizontalUrl': 'https://www.helloasso.com/associations/permaculture-catalane/adhesions/adhesion-a-l-association-2/widget-vignette-horizontale', 'widgetVignetteVerticalUrl': 'https://www.helloasso.com/associations/permaculture-catalane/adhesions/adhesion-a-l-association-2/widget-vignette', 'formSlug': 'adhesion-a-l-association-2', 'formType': 'Membership', 'url': 'https://www.helloasso.com/associations/permaculture-catalane/adhesions/adhesion-a-l-association-2', 'organizationSlug': 'permaculture-catalane'}, {'currency': 'EUR', 'meta': {'createdAt': '2021-08-17T12:52:55.457+02:00', 'updatedAt': '2022-01-11T12:11:05.507+01:00'}, 'state': 'Public', 'title': 'Faire un don au développeur web ', 'privateTitle': 'Soutien au développeur du site web', 'widgetButtonUrl': 'https://www.helloasso.com/associations/permaculture-catalane/formulaires/3/widget-bouton', 'widgetFullUrl': 'https://www.helloasso.com/associations/permaculture-catalane/formulaires/3/widget', 'formSlug': '3', 'formType': 'Donation', 'url': 'https://www.helloasso.com/associations/permaculture-catalane/formulaires/3', 'organizationSlug': 'permaculture-catalane'}, {'currency': 'EUR', 'description': 'Financement du stage de Eloi pour apprendre la gouvernance partagée', 'endDate': '2021-07-31T00:00:00+02:00', 'meta': {'createdAt': '2021-07-15T10:10:43.653+02:00', 'updatedAt': '2022-07-11T12:36:30.24+02:00'}, 'state': 'Public', 'title': 'Financement de stage de gouvernance partagée', 'widgetButtonUrl': 'https://www.helloasso.com/associations/permaculture-catalane/collectes/financement-de-stage-de-gouvernance-partagee/widget-bouton', 'widgetFullUrl': 'https://www.helloasso.com/associations/permaculture-catalane/collectes/financement-de-stage-de-gouvernance-partagee/widget', 'widgetVignetteHorizontalUrl': 'https://www.helloasso.com/associations/permaculture-catalane/collectes/financement-de-stage-de-gouvernance-partagee/widget-vignette-horizontale', 'widgetVignetteVerticalUrl': 'https://www.helloasso.com/associations/permaculture-catalane/collectes/financement-de-stage-de-gouvernance-partagee/widget-vignette', 'formSlug': 'financement-de-stage-de-gouvernance-partagee', 'formType': 'CrowdFunding', 'url': 'https://www.helloasso.com/associations/permaculture-catalane/collectes/financement-de-stage-de-gouvernance-partagee', 'organizationSlug': 'permaculture-catalane'}, {'currency': 'EUR', 'meta': {'createdAt': '2021-04-30T20:06:38.247+02:00', 'updatedAt': '2022-06-14T18:26:38.44+02:00'}, 'state': 'Private', 'title': 'Checkout', 'formSlug': 'default', 'formType': 'Checkout', 'url': 'https://www.helloasso.com/associations/permaculture-catalane/checkout', 'organizationSlug': 'permaculture-catalane'}, {'banner': {'fileName': 'fond-formulaire-59ed5510c86c47f19e58136a018cfe68.png?bb=0x0x1920x1080&sb=1920x1080', 'publicUrl': 'https://cdn.helloasso.com/img/photos/collectes/fond-formulaire-59ed5510c86c47f19e58136a018cfe68.png?bb=0x0x1920x1080&sb=1920x1080'}, 'currency': 'EUR', 'meta': {'createdAt': '2020-11-26T01:24:12.7+01:00', 'updatedAt': '2022-01-19T14:09:21.18+01:00'}, 'state': 'Public', 'title': 'SOUTENEZ PERMAculture CATalane,SAUVEZ LES #Liensde1èreNécessité !', 'privateTitle': 'SOUTENEZ PERMAculture CATalane, SAUVEZ LES #Liensde1èreNécessité!', 'widgetButtonUrl': 'https://www.helloasso.com/associations/permaculture-catalane/formulaires/2/widget-bouton', 'widgetFullUrl': 'https://www.helloasso.com/associations/permaculture-catalane/formulaires/2/widget', 'formSlug': '2', 'formType': 'Donation', 'url': 'https://www.helloasso.com/associations/permaculture-catalane/formulaires/2', 'organizationSlug': 'permaculture-catalane'}, {'currency': 'EUR', 'startDate': '2021-01-01T00:00:00+00:00', 'endDate': '2021-12-31T23:59:59.999+00:00', 'meta': {'createdAt': '2019-08-23T14:51:35.47+02:00', 'updatedAt': '2022-01-11T11:13:25.113+01:00'}, 'state': 'Public', 'title': "Adhésion à l'association 2021", 'widgetButtonUrl': 'https://www.helloasso.com/associations/permaculture-catalane/adhesions/adhesion-a-l-association/widget-bouton', 'widgetFullUrl': 'https://www.helloasso.com/associations/permaculture-catalane/adhesions/adhesion-a-l-association/widget', 'widgetVignetteHorizontalUrl': 'https://www.helloasso.com/associations/permaculture-catalane/adhesions/adhesion-a-l-association/widget-vignette-horizontale', 'widgetVignetteVerticalUrl': 'https://www.helloasso.com/associations/permaculture-catalane/adhesions/adhesion-a-l-association/widget-vignette', 'formSlug': 'adhesion-a-l-association', 'formType': 'Membership', 'url': 'https://www.helloasso.com/associations/permaculture-catalane/adhesions/adhesion-a-l-association', 'organizationSlug': 'permaculture-catalane'}, {'currency': 'EUR', 'meta': {'createdAt': '2019-08-23T14:14:36.837+02:00', 'updatedAt': '2022-01-21T03:35:17.11+01:00'}, 'state': 'Public', 'title': 'Faire un don à PERMAculture CATalane', 'privateTitle': "Financement de l'association", 'widgetButtonUrl': 'https://www.helloasso.com/associations/permaculture-catalane/formulaires/1/widget-bouton', 'widgetFullUrl': 'https://www.helloasso.com/associations/permaculture-catalane/formulaires/1/widget', 'formSlug': '1', 'formType': 'Donation', 'url': 'https://www.helloasso.com/associations/permaculture-catalane/formulaires/1', 'organizationSlug': 'permaculture-catalane'}], 'pagination': {'pageSize': 20, 'totalCount': 8, 'pageIndex': 1, 'totalPages': 1, 'continuationToken': '20190823121436837'}}

    def getForm(type, slug):
        url = "https://api.helloasso.com/v5/organizations/" + pcat_slug + "/forms/"+type+"/"+slug+"/public"
        headers = {"authorization": "Bearer "+ accessStoken["access_token"]}
        reponse = requests.get(url, headers=headers)
        data = simplejson.loads(reponse.text)
        print(data)

    def getFormAdhesions2022():
        getForm(type="Membership", slug="adhesion-a-l-association-2")

    #form_adhesions = getFormAdhesions2022()
    form_adhesions = {'organizationName': 'PERMAculture CATalane', 'tiers': [{'id': 5671289, 'label': 'Devenir adhérent', 'description': '', 'tierType': 'Membership', 'price': 500, 'vatRate': 0.0, 'paymentFrequency': 'Single', 'isEligibleTaxReceipt': False}], 'activityType': 'Cotisation', 'activityTypeId': 2908, 'validityType': 'Custom', 'currency': 'EUR', 'startDate': '2022-01-01T00:00:00+00:00', 'endDate': '2023-01-31T23:59:59.999+00:00', 'meta': {'createdAt': '2022-01-11T11:11:10.8557294+01:00', 'updatedAt': '2022-01-11T21:38:33.9066667+01:00'}, 'state': 'Public', 'title': "Adhésion à l'association 2022", 'widgetButtonUrl': 'https://www.helloasso.com/associations/permaculture-catalane/adhesions/adhesion-a-l-association-2/widget-bouton', 'widgetFullUrl': 'https://www.helloasso.com/associations/permaculture-catalane/adhesions/adhesion-a-l-association-2/widget', 'widgetVignetteHorizontalUrl': 'https://www.helloasso.com/associations/permaculture-catalane/adhesions/adhesion-a-l-association-2/widget-vignette-horizontale', 'widgetVignetteVerticalUrl': 'https://www.helloasso.com/associations/permaculture-catalane/adhesions/adhesion-a-l-association-2/widget-vignette', 'formSlug': 'adhesion-a-l-association-2', 'formType': 'Membership', 'url': 'https://www.helloasso.com/associations/permaculture-catalane/adhesions/adhesion-a-l-association-2', 'organizationSlug': 'permaculture-catalane'}







