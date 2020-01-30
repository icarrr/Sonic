import onedrivesdk

redirect_uri = 'http://localhost:8080/'
client_secret = 'l2ou?5xzD3:mHa0zTXkiPF-xB-?OUA]U'
client_id='9e62671f-d2e8-44c2-93b3-082c4e14b13e'
api_base_url='https://api.onedrive.com/v1.0/'
scopes=['wl.signin', 'wl.offline_access', 'onedrive.readwrite']

http_provider = onedrivesdk.HttpProvider()
auth_provider = onedrivesdk.AuthProvider(
    http_provider=http_provider,
    client_id=client_id,
    scopes=scopes)

client = onedrivesdk.OneDriveClient(api_base_url, auth_provider, http_provider)
auth_url = client.auth_provider.get_auth_url(redirect_uri)
# Ask for the code
print('Paste this URL into your browser, approve the app\'s access.')
print('Copy everything in the address bar after "code=", and paste it below.')
print(auth_url)
code = input('Paste code here: ')

client.auth_provider.authenticate(code, redirect_uri, client_secret)

f = onedrivesdk.Folder()
i = onedrivesdk.Item()
i.name = 'New Folder'
i.folder = f

returned_item = client.item(drive='me', id='root').children.add(i)
