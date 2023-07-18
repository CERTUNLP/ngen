from constance import config
from cortex4py.api import Api
from cortex4py.exceptions import NotFoundError, CortexException, AuthenticationError
from cortex4py.models import Organization, User

CORTEX_HOST = f'http://{config.CORTEX_HOST}'
try:
    api = Api(CORTEX_HOST, config.CORTEX_APIKEY)
    api.status()
except CortexException:
    api = None
    api_user = None

if api:
    try:
        org = api.organizations.get_by_id('ngen org')
    except NotFoundError:
        org = api.organizations.create(Organization({
            "name": "ngen org",
            "description": "ngen default organization",
        }))
    except AuthenticationError:
        org = None
        api = None

    if org:
        try:
            user = api.users.get_by_id('user')
        except NotFoundError:
            user = api.users.create(User({
                'login': 'user',
                'name': 'user',
                'roles': ['read', 'analyze', 'orgadmin'],
                'status': 'Ok',
                'organization': 'ngen org'
            }))

            api.users.set_password(user.id, 'user')
            api.users.set_key(user.id)

        default_analyzer_conf = {
            "configuration": {
                "auto_extract_artifacts": True,
                "check_tlp": True,
                "check_pap": True,
                "max_tlp": 2,
                "max_pap": 2
            },
            "jobCache": 10080,
            "jobTimeout": 30,
        }
        api_user = Api(CORTEX_HOST, api.users.get_key(user.id))

        for analyzer in api_user.analyzers.definitions():
            if not analyzer.configurationItems and not api_user.analyzers.get_by_name(analyzer.id):
                api_user.analyzers.enable(analyzer.id, default_analyzer_conf)
