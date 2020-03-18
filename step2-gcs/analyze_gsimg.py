# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

'''
analyze_gsimg.py - analyze G Suite image processing workflow

Download image from Google Drive, archive to Google Cloud Storage, send
to Google Cloud Vision for processing, add results row to Google Sheet.
'''

from __future__ import print_function
import io

from googleapiclient import discovery, http
from httplib2 import Http
from oauth2client import file, client, tools

FILE = 'YOUR_IMG_ON_DRIVE'
BUCKET = 'YOUR_BUCKET_NAME'
PARENT = ''     # YOUR IMG FILE PREFIX

# process credentials for OAuth2 tokens
SCOPES = (
    'https://www.googleapis.com/auth/drive.readonly',
    'https://www.googleapis.com/auth/devstorage.full_control',
)
store = file.Storage('storage.json')
creds = store.get()
if not creds or creds.invalid:
    flow = client.flow_from_clientsecrets('client_secret.json', SCOPES)
    creds = tools.run_flow(flow, store)

# create API service endpoints
HTTP = creds.authorize(Http())
DRIVE  = discovery.build('drive',   'v3', http=HTTP)
GCS    = discovery.build('storage', 'v1', http=HTTP)


def drive_get_img(fname):
    'download file from Drive and return file info & binary if found'

    # search for file on Google Drive
    rsp = DRIVE.files().list(q="name='%s'" % fname,
            fields='files(id,name,mimeType,modifiedTime)'
    ).execute().get('files', [])

    # download binary & return file info if found, else return None
    if rsp:
        target = rsp[0]  # use first matching file
        fileId = target['id']
        fname = target['name']
        mtype = target['mimeType']
        binary = DRIVE.files().get_media(fileId=fileId).execute()
        return fname, mtype, target['modifiedTime'], binary


def gcs_blob_upload(fname, bucket, media, mimetype):
    'upload an object to a Google Cloud Storage bucket'

    # build blob metadata and upload via GCS API
    body = {'name': fname, 'uploadType': 'multipart', 'contentType': mimetype}
    return GCS.objects().insert(bucket=bucket, body=body,
            media_body=http.MediaIoBaseUpload(io.BytesIO(media), mimetype),
            fields='bucket,name').execute()


if __name__ == '__main__':
    # download img file & info from Drive
    rsp = drive_get_img(FILE)
    if rsp:
        fname, mtype, ftime, data = rsp
        print('Downloaded %r (%s, %s, size: %d)' % (fname, mtype, ftime, len(data)))

        # upload file to GCS
        gcsname = '%s/%s'% (PARENT, fname)
        rsp = gcs_blob_upload(gcsname, BUCKET, data, mtype)
        if rsp:
            print('Uploaded %r to GCS bucket %r' % (rsp['name'], rsp['bucket']))
        else:
            print('ERROR: Cannot upload %r to Cloud Storage' % gcsname)
    else:
        print('ERROR: Cannot download %r from Drive' % fname)
