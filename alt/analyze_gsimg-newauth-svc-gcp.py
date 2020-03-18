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
import argparse
import webbrowser

from googleapiclient import discovery
import google.auth
from google.cloud import storage, vision

k_ize = lambda b: '%6.2fK' % (b/1000.) # bytes to kBs
FILE = 'YOUR_IMG_ON_DRIVE'
BUCKET = 'YOUR_BUCKET_NAME'
PARENT = ''     # YOUR IMG FILE PREFIX
SHEET = 'YOUR_SHEET_ID'
TOP = 5       # TOP # of VISION LABELS TO SAVE
DEBUG = False

# create API service endpoints
creds, _proj_id = google.auth.default()
DRIVE  = discovery.build('drive',   'v3', credentials=creds)
GCS    = storage.Client()
VISION = vision.ImageAnnotatorClient()
SHEETS = discovery.build('sheets',  'v4', credentials=creds)


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
    blob = GCS.bucket(bucket).blob(fname)
    blob.upload_from_string(media, mimetype)
    return {'bucket': bucket, 'name': fname}


def vision_label_img(img, top):
    'send image to Vision API for label annotation'

    # call Vision API to process
    image = vision.types.Image(content=img)
    labels = VISION.label_detection(image=image, max_results=top).label_annotations

    # return top labels for image as CSV for Sheet (row)
    return ', '.join('(%.2f%%) %s' % (
            label.score*100., label.description) for label in labels)


def sheet_append_row(sheet, row):
    'append row to a Google Sheet, return #cells added'

    # call Sheets API to write row to Sheet (via its ID)
    rsp = SHEETS.spreadsheets().values().append(
            spreadsheetId=sheet, range='Sheet1',
            valueInputOption='USER_ENTERED', body={'values': [row]}
    ).execute()
    if rsp:
        return rsp.get('updates').get('updatedCells')


def main(fname, bucket, sheet_id, folder, top, debug):
    '"main()" drives process from image download through report generation'

    # download img file & info from Drive
    rsp = drive_get_img(fname)
    if not rsp:
        return
    fname, mtype, ftime, data = rsp
    if debug:
        print('Downloaded %r (%s, %s, size: %d)' % (fname, mtype, ftime, len(data)))

    # upload file to GCS
    gcsname = '%s/%s'% (folder, fname)
    rsp = gcs_blob_upload(gcsname, bucket, data, mtype)
    if not rsp:
        return
    if debug:
        print('Uploaded %r to GCS bucket %r' % (rsp['name'], rsp['bucket']))

    # process w/Vision
    rsp = vision_label_img(data, top)
    if not rsp:
        return
    if debug:
        print('Top %d labels from Vision API: %s' % (top, rsp))

    # push results to Sheet, get cells-saved count
    fsize = k_ize(len(data))
    row = [folder,
            '=HYPERLINK("storage.cloud.google.com/%s/%s", "%s")' % (
            bucket, gcsname, fname), mtype, ftime, fsize, rsp
    ]
    rsp = sheet_append_row(sheet_id, row)
    if not rsp:
        return
    if debug:
        print('Added %d cells to Google Sheet' % rsp)
    return True


if __name__ == '__main__':
    # args: [-hv] [-i imgfile] [-b bucket] [-f folder] [-s Sheet ID] [-t top labels]
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--imgfile", action="store_true",
            default=FILE, help="image file filename")
    parser.add_argument("-b", "--bucket_id", action="store_true",
            default=BUCKET, help="Google Cloud Storage bucket name")
    parser.add_argument("-f", "--folder", action="store_true",
            default=PARENT, help="Google Cloud Storage image folder")
    parser.add_argument("-s", "--sheet_id", action="store_true",
            default=SHEET, help="Google Sheet Drive file ID (44-char str)")
    parser.add_argument("-t", "--viz_top", action="store_true",
            default=TOP, help="return top N (default %d) Vision API labels" % TOP)
    parser.add_argument("-v", "--verbose", action="store_true",
            default=DEBUG, help="verbose display output")
    args = parser.parse_args()

    print('Processing file %r... please wait' % args.imgfile)
    rsp = main(args.imgfile, args.bucket_id,
            args.sheet_id, args.folder, args.viz_top, args.verbose)
    if rsp:
        sheet_url = 'https://docs.google.com/spreadsheets/d/%s/edit' % args.sheet_id
        print('DONE: opening web browser to it, or see %s' % sheet_url)
        webbrowser.open(sheet_url, new=1, autoraise=True)
    else:
        print('ERROR: could not process %r' % args.imgfile)
