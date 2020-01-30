import json
import re
import onedrivesdk
import requests
from onedrivesdk.helpers.resource_discovery import ResourceDiscoveryRequest, \
    ServiceInfo

# our domain (not the original)
redirect_uri = 'http://localhost:8080'
# our client id (not the original)
client_id = "9e62671f-d2e8-44c2-93b3-082c4e14b13e"
# our client secret (not the original)
client_secret = 'l2ou?5xzD3:mHa0zTXkiPF-xB-?OUA]U'
resource = 'https://api.office.com/discovery/'
auth_server_url = 'https://login.microsoftonline.com/common/oauth2/authorize'
auth_token_url = 'https://login.microsoftonline.com/common/oauth2/token'

# our sharepoint URL (not the original)
sharepoint_base_url = 'https://mannfc88.sharepoint.com/'
# our site URL (not the original)
sharepoint_site_url = sharepoint_base_url + 'sites/siBunglonLabs'

file_to_upload = 'tmp/test.xlsx'
target_filename = 'test.xlsx'


class AnyVersionResourceDiscoveryRequest(ResourceDiscoveryRequest):

    def get_all_service_info(self, access_token, sharepoint_base_url):
        headers = {'Authorization': 'Bearer ' + access_token}
        response = json.loads(requests.get(self._discovery_service_url,
                                           headers=headers).text)
        service_info_list = [ServiceInfo(x) for x in response['value']]
        # Get all services, not just the ones with service_api_version 'v2.0'
        # Filter only on service_resource_id
        sharepoint_services = \
            [si for si in service_info_list
             if si.service_resource_id == sharepoint_base_url]
        return sharepoint_services


http = onedrivesdk.HttpProvider()
auth = onedrivesdk.AuthProvider(http_provider=http, client_id=client_id,
                                auth_server_url=auth_server_url,
                                auth_token_url=auth_token_url)

should_authenticate_via_browser = False
try:
    # Look for a saved session. If not found, we'll have to
    # authenticate by opening the browser.
    auth.load_session()
    auth.refresh_token()
except FileNotFoundError as e:
    should_authenticate_via_browser = True
    pass

if should_authenticate_via_browser:
    auth_url = auth.get_auth_url(redirect_uri)
    code = ''
    while not re.match(r'[a-zA-Z0-9_-]+', code):
        # Ask for the code
        print('Paste this URL into your browser, approve the app\'s access.')
        print('Copy the resulting URL and paste it below.')
        print(auth_url)
        code = input('Paste code here: ')
        # Parse code from URL if necessary
        if re.match(r'.*?code=([a-zA-Z0-9_-]+).*', code):
            code = re.sub(r'.*?code=([a-zA-Z0-9_-]*).*', r'\1', code)

    auth.authenticate(code, redirect_uri, client_secret, resource=resource)
    service_info = AnyVersionResourceDiscoveryRequest().\
        get_all_service_info(auth.access_token, sharepoint_base_url)[0]
    auth.redeem_refresh_token(service_info.service_resource_id)
    auth.save_session()

client = onedrivesdk.OneDriveClient(sharepoint_site_url + '/_api/v2.0/',
                                    auth, http)
# Get the drive ID of the Documents folder.
documents_drive_id = [x['id']
                      for x
                      in client.drives.get()._prop_list
                      if x['name'] == 'Documents'][0]
items = client.item(drive=documents_drive_id, id='root')
# Upload file
uploaded_file_info = items.children[target_filename].upload(file_to_upload)
