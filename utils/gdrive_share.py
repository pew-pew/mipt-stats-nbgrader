import os.path
import pathlib
import urllib

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

creds_path = str(pathlib.Path(__file__).absolute().parent / "credentials.json")

SCOPES = ['https://www.googleapis.com/auth/drive']

def get_creds():
    # https://developers.google.com/drive/api/quickstart/python
    """Shows basic usage of the Drive v3 API.
    Prints the names and ids of the first 10 files the user has access to.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                creds_path, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds


def parse_gdrive_folder_id(url_or_folderid):
    if "/" not in url_or_folderid:
        return url_or_folderid
    url = url_or_folderid
    parsed = urllib.parse.urlparse(url)
    if parsed.netloc != "drive.google.com":
        raise ValueError(f"Invalid gdrive folder url {url!r}")
    parts = parsed.path.split("/")
    if len(parts) < 2 or parts[-2] != "folders":
        raise ValueError(f"Invalid gdrive folder url {url!r}")
    return parts[-1]


SERVICE = None

def upload_and_share(local_path, remote_name, folder):
    global SERVICE
    if SERVICE is None:
        SERVICE = build('drive', 'v3', credentials=get_creds())
    
    folder_id = parse_gdrive_folder_id(folder)
    
    file_metadata = {'name': remote_name, "parents": [folder_id]}
    media = MediaFileUpload(local_path, mimetype='text/plain')
    file = SERVICE.files().create(
        body=file_metadata,
        media_body=media,
        fields='id',
    ).execute()
    file_id = file["id"]

    SERVICE.permissions().create(fileId=file_id, body={
        'type': 'anyone',
        'role': 'reader',
        'allowFileDiscovery': False,
    }).execute()

    return f"https://drive.google.com/file/d/{file_id}/view"
