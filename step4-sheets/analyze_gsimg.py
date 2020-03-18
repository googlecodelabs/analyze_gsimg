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
import base64
import io

from googleapiclient import discovery, http
from httplib2 import Http
from oauth2client import file, client, tools

k_ize = lambda b: '%6.2fK' % (b/1000.) # bytes to kBs
FILE = 'YOUR_IMG_ON_DRIVE'
BUCKET = 'YOUR_BUCKET_NAME'
PARENT = ''     # YOUR IMG FILE PREFIX
SHEET = 'YOUR_SHEET_ID'
TOP = 5       # TOP # of VISION LABELS TO SAVE

# process credentials for OAuth2 tokens
SCOPES = (
    'https://www.googleapis.com/auth/drive.readonly',
    'https://www.googleapis.com/auth/devstorage.full_control',
    'https://www.googleapis.com/auth/cloud-vision',
    'https://www.googleapis.com/auth/spreadsheets',
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
VISION = discovery.build('vision',  'v1', http=HTTP)
SHEETS = discovery.build('sheets',  'v4', http=HTTP)


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


def vision_label_img(img, top):
    'send image to Vision API for label annotation'

    # build image metadata and call Vision API to process
    body = {'requests': [{
                'image':     {'content': img},
                'features': [{'type': 'LABEL_DETECTION', 'maxResults': top}],
    }]}
    rsp = VISION.images().annotate(body=body).execute().get('responses', [{}])[0]

    # return top labels for image as CSV for Sheet (row)
    if 'labelAnnotations' in rsp:
        return ', '.join('(%.2f%%) %s' % (
                label['score']*100., label['description']) \
                for label in rsp['labelAnnotations'])


def sheet_append_row(sheet, row):
    'append row to a Google Sheet, return #cells added'

    # call Sheets API to write row to Sheet (via its ID)
    rsp = SHEETS.spreadsheets().values().append(
            spreadsheetId=sheet, range='Sheet1',
            valueInputOption='USER_ENTERED', body={'values': [row]}
    ).execute()
    if rsp:
        return rsp.get('updates').get('updatedCells')


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

            # process w/Vision
            rsp = vision_label_img(base64.b64encode(data).decode('utf-8'), TOP)
            if rsp:
                print('Top %d labels from Vision API: %s' % (TOP, rsp))

                # push results to Sheet, get cells-saved count
                fsize = k_ize(len(data))
                row = [PARENT,
                        '=HYPERLINK("storage.cloud.google.com/%s/%s", "%s")' % (
                        BUCKET, gcsname, fname), mtype, ftime, fsize, rsp
                ]
                rsp = sheet_append_row(SHEET, row)
                if rsp:
                    print('Updated %d cells in Google Sheet' % rsp)
                else:
                    print('ERROR: Cannot write row to Google Sheets')
            else:
                print('ERROR: Vision API cannot analyze %r' % fname)
        else:
            print('ERROR: Cannot upload %r to Cloud Storage' % gcsname)
    else:
        print('ERROR: Cannot download %r from Drive' % fname)
