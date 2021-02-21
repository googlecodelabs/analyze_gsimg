# Cloud image processing workflow:
### Image archive, analysis, and report generation with Google Workspace (formerly G Suite) & GCP

In the [intermediate codelab tutorial](http://g.co/codelabs/drive-gcs-vision-sheets), developers build a cloud-based image processing workflow in Python along with Google Cloud REST APIs from [GCP](http://cloud.google.com) and [Google Workspace (formerly G Suite)](http://developers.google.com/gsuite). The exercise imagines an enterprise scenario where an organization can backup data (image files, for example) to the cloud, analyze them with machine learning, and report results formatted for consumption by management. This repo provides code solutions for each step through the tutorial plus alternate versions featuring other libraries and/or authorization schemes.

This is an intermediate codelab. If you're new to using Google APIs, specifically Google Workspace (formerly G Suite) and/or GCP APIs, we recommend completing the introductory codelabs (listed at the bottom of this page) first.


## Prerequisites

- A Google account (Google Workspace/G Suite accounts may require administrator approval)
- A Google Cloud Platform project with an active billing account
- Familiarity with operating system terminal/shell commands
- Basic skills in [Python](http://python.org) 2 or 3 ([other languages supported](http://developers.google.com/api-client-library))
- Experience using Google APIs may be helpful but not required

> **NOTE for GCP developers**:
> The codelab does not use GCP [*product* client libraries](https://cloud.google.com/apis/docs/cloud-client-libraries) nor _service account_ authorization — instead it uses the lower-level *platform* client libraries (because non-Cloud APIs don't have product libraries yet) and _user account_ authorization (because the target file starts out in Google Drive). However, solutions featuring GCP product client libraries as well as service accounts are available as alternatives in the [`alt`](alt) folder.


## Description

The primary objective is to **analyze Google Workspace images**... everything else (archiving, report generation) is a bonus. It starts with the image file on Google Drive, archives it to Google Cloud Storage, analyzes it with Cloud Vision, and writes a "results" row into a Google Sheet. Each step of the tutorial builds successively on the previous step, adding one feature at a time. Each of the `step*` directories represent the state the application should be in upon successful completion of that corresponding step in the codelab, culminating with a refactor step to arrive at the `final` version.

1. **Download image from Google Drive**
 The first step utilizes the [Google Drive API](https://developers.google.com/drive) to search for the image file and downloads the first match. Along with the filename and binary payload, the file's MIMEtype, last modification timestamp, and size in bytes are also returned.

1. **Backup image to Google Cloud Storage**
 The next step is to upload the image as a "blob" [object](https://cloud.google.com/storage/docs/key-terms#objects) to [Google Cloud Storage](https://cloud.google.com/storage) (GCS), performing an "insert" to the given [bucket](https://cloud.google.com/storage/docs/key-terms#buckets). Once data is in GCS, it can then be used by other GCP tools. GCS also supports cheaper, "colder" storage, meaning the less often you access objects, the lower the cost, as described on the [storage class page](https://cloud.google.com/storage/docs/storage-classes). NOTE: "/" in GCS filenames is merely a visual cue as GCS doesn't support "folders." Our solution features an optional `PARENT` folder to help organize images in the destination bucket. (The GCP client libraries prep the data for GCS, so we need the *platform* client library [`MediaIoBaseUpload`](https://googleapis.github.io/google-api-python-client/docs/epy/googleapiclient.http.MediaIoBaseUpload-class.html) convenience object to help with the upload using the platform library.)

1. **Send image to Cloud Vision for analysis**
 Since we have the image binary data, let's also send it to [Cloud Vision](https://cloud.google.com/vision) for analysis. Using its API, request object detection/identification (called [_label annotation_](https://cloud.google.com/vision/docs/labels)), but ask only for the top 5 labels for a faster response. Each label returned includes a confidence score the label applies to the image.

1. **Add results to Google Sheets**
 The last new feature is report generation: add a spreadsheet row to visualize results via the [Google Sheets API](https://developers.google.com/sheets). The row includes the Cloud Vision output and the file's GCS archive hyperlinked location.

1. \***Refactor**
 The final, yet optional, step involves refactoring with best practices: move the "main" body into a separate function and supporting command-line options to provide user flexibility.


## Authorization scheme and alternative versions

We've selected to use *user account authorization* (instead of *service account authorization*), *platform* client libraries (instead of *product* client libraries since those aren't available for Google Workspace (formerly G Suite) APIs), and older auth libraries for readability, consistency, greater Python 2-3 compatibility, and automated OAuth2 token management. This provides what we hope is the least complex user experience. Alternative versions (of the final application) using service accounts, product client libraries, and newer currently-supported auth libraries, are found in the [`alt`](alt) subdirectory. See its [README](alt/README.md) for more information.


## Summary and further study

The goal of the codelab sample app is to help developers envision possible business scenarios. A secondary goal is showing how to use GCP and Google Workspace (formerly G Suite) APIs together for one solution. Problems with either the codelab or code in this repo? [File an issue](https://github.com/googlecodelabs/feedback/issues/new?title=[drive-gcs-vision-sheets]:&labels[]=content-platform&labels[]=cloud,python) (do a search first).


# References

- Codelabs
    - [Intro to Google Workspace (formerly G Suite) APIs (Google Drive API)](http://g.co/codelabs/gsuite-apis-intro) (Python)
    - [Using Cloud Vision with Python](http://g.co/codelabs/vision-python) (Python)
    - [Build customized reporting tools (Google Sheets API)](http://g.co/codelabs/sheets) (JS/Node)
    - [Upload objects to Google Cloud Storage](http://codelabs.developers.google.com/codelabs/cloud-upload-objects-to-cloud-storage) (no coding required)
- General
    - [Google APIs client library for Python](https://developers.google.com/api-client-library/python)
    - [Google APIs client libraries](https://developers.google.com/api-client-library)
- Google Workspace (formerly G Suite)
    - [Google Drive API home page](https://developers.google.com/drive)
    - [Google Sheets API home page](https://developers.google.com/sheets)
    - [Google Workspace (formerly G Suite) developer overview & documentation](https://developers.google.com/gsuite).
- Google Cloud Platform (GCP)
    - [Google Cloud Storage home page](https://cloud.google.com/storage)
    - [Google Cloud Vision home page & live demo](https://cloud.google.com/vision)
        - [Cloud Vision API documentation](https://cloud.google.com/vision/docs)
        - [Vision API image labeling docs](https://cloud.google.com/vision/docs/labels)
    - [Python on the Google Cloud Platform](https://cloud.google.com/python)
    - [GCP product client libraries](https://cloud.google.com/apis/docs/cloud-client-libraries)
    - [GCP documentation](https://cloud.google.com/docs)
