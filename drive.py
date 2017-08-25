#!/usr/bin/python

"""Google Drive Quickstart in Python.

This script uploads a single file to Google Drive.
"""

import pprint

import httplib2
import apiclient.discovery
import apiclient.http
import oauth2client.client

# Check https://developers.google.com/drive/scopes for all available scopes.
OAUTH2_SCOPE = 'https://www.googleapis.com/auth/drive'

# Location of the client secrets.
CLIENT_SECRETS = '../client_secret.json'

# Path to the file to upload.
FILENAME = 'arthasastra.db'

# Metadata about the file.
MIMETYPE = 'text/plain'
TITLE = 'ArthaSastra Backup'
DESCRIPTION = 'Backup of arthasastra.db'

# OAuth 2.0 scope that will be authorized.
class GoogleDrive(object):
    def __init__(self):
        # Perform OAuth2.0 authorization flow.
        self.flow = oauth2client.client.flow_from_clientsecrets(CLIENT_SECRETS, OAUTH2_SCOPE)
        self.flow.redirect_uri = oauth2client.client.OOB_CALLBACK_URN
        self.authorize_url = self.flow.step1_get_authorize_url()
    def OauthURL(self):
        return self.authorize_url
    def upload(self,code):
        code = code.strip()
        credentials = self.flow.step2_exchange(code)

        # Create an authorized Drive API client.
        http = httplib2.Http()
        credentials.authorize(http)
        drive_service = apiclient.discovery.build('drive', 'v2', http=http)

        # Insert a file. Files are comprised of contents and metadata.
        # MediaFileUpload abstracts uploading file contents from a file on disk.
        media_body = apiclient.http.MediaFileUpload(
            FILENAME,
            mimetype=MIMETYPE,
            resumable=True
        )
        # The body contains the metadata for the file.
        body = {
          'title': TITLE,
          'description': DESCRIPTION,
        }

        # Perform the request and print the result.
        new_file = drive_service.files().insert(body=body, media_body=media_body).execute()
        pprint.pprint(new_file)

if __name__ == "__main__":
    GD = GoogleDrive()
    print(GD.OauthURL())
    GD.upload(input())
