# Cloud image processing workflow:
### Image archive, analysis, and report generation with G Suite & GCP

Get the best of both sides of Google Cloud by using both GCP & G Suite RESTful APIs to analyze and backup images from G Suite using GCP and collating the results back into G Suite. This repo holds the code samples which are part of [its corresponding codelab](http://g.co/codelabs/drive-gcs-vision-sheets).

## Prerequisites

- A Google account (G Suite accounts may require administrator approval)
- A Google Cloud Platform project
- An active GCP billing account
- A modern web browser such Chrome or Firefox
- Basic Python skills; this exercise requires Python 3.6+. (It is possible to backport the code to 2.x provided you have the requisite libraries but recommend moving to 3.x as soon as possible.)

This codelab exercise is built with Python, but [Google APIs client libraries](https://developers.google.com/api-client-library) are available in most of the common languages (Node/JS, Java, C#, PHP, Ruby, etc.) allowing you to build an equivalent version in your preferred development environment.

Be sure to have the appropriate client library installed before you tackle this codelab as they're required for you to communicate with all the Google APIs used in this exercise. For Python users, issue a command like this to install it: `pip3 install -U google-api-python-client` (or `pip3` if you have a mixed environment). We made the deliberate decision to use these low-level platform client libraries because they work across different families of Google APIs.

Developers may be familiar with the GCP [higher-level *product* client libraries](https://cloud.google.com/apis/docs/cloud-client-libraries) but chose consistency over convenience in selecting the lower-level libraries. A solution using the high-level GCP product client libraries is available in the `alt` directory of [this codelab's open-source repo](https://github.com/googlecodelabs/drive-gcs-vision-sheets) for those who prefer it. Of course to run those samples, you would need to have *those* client libraries installed to use them.


## Description

Get the best of both sides of Google Cloud with GCP & G Suite. Learn how to download images from Google Drive, back them up to Google Cloud Storage, analyze them with the Google Cloud Vision API, and generate a report of the results as a Google Sheets spreadsheet. Also see the PC102 talk at Google Cloud NEXT '20 where the code featured in this codelab plays a major role.

The [Google Cloud Vision API](https://cloud.google.com/vision)
allows developers to easily integrate vision detection features within applications, including image labeling, facial features detection, landmark detection, optical character recognition (OCR), "safe search," or tagging of explicit content, detecting product or corporate logos, and several others.

This repository consists of the sample apps that are part of the [https://codelabs.developers.google.com/codelabs/cloud-vision-api-python]("Using the Vision API with Python" hands-on codelab). That codelab teaches developers how to use some of the features described above with the Cloud Vision API using Python, namely label annotations, OCR/text extraction, landmark detection, and detecting facial features! As described above, there are 4 main steps developers take as part of this codelab:

### Download image file from Google Drive

The first step is to use the Google Drive API to search for an image file name, and download the first matching file it finds. In addition to the filename and the file's binary payload, some additional information is also needed for the succeeding steps: the file's MIMEtype, the timestamp of its most recent modification, and the size of the file.

### Backup image file to Google Cloud Storage

The next step is to upload the file contents as a "blob" object to Google Cloud Storage. This is done by using its API to perform an "object insert" request along with the [bucket]() name you wish the file stored. The return values from this call include the full name of the object (including any prepended "directory" paths as well as the bucket to which the blob was uploaded to. Since Cloud Storage does not support the abstraction of a filesystem, there's no concept of directories or folders, so just consider the "/" character as any other in a file's pathname. The solution supports zero or one folder name prepended with "/" along with the actual filename.

One primary reason to consider uploading files to Cloud Storage is to backup your data. Another reason would be that Cloud Storage supports cheaper, "colder" storage, meaning the less you access objects, the less it costs to store it. Cloud Storage supports [four different storage classes](https://cloud.google.com/storage/docs/storage-classes), each with different access availability levels and corresponding costs.


### Send image file to Cloud Vision for analysis

Since we have the file's binary when backing up to Cloud Storage, we can use the same content to request for its analysis by the Cloud Vision service. Using its API, the code in this step requests object identification or label annotation. The API will do its best, using a proprietary pre-trained model to determine what objects are found in the image as well as a confidence score (as a percentage) that the object is found there. To ensure a speedy reply, the code sample asks for only the top 5 labels found by Cloud Vision returned along with those confidence scores.


### Generate report with results in Google Sheets

At the end of your journey is what to show your manager. A spreadsheet is a great way to summarize data with quantitative values. The Google Sheet generated in this step contains the (fake) "folder" name (if you chose one), the actual filename, its MIMEtype, the last modified timestamp, the file size, and the top 5 labels from Cloud Vision prepended with in descending order of confidence score. Furthermore, the filename will be hyperlinked to its newly-created location in Cloud Storage.

## Summary and further study


As mentioned above, the `alt` contains several alternative versions of the final version of the main script from this codelab. Specifically they use other supporting auth and client libraries that are part of the Google developer ecosystem. Not everyone uses the same libraries, and becoming familiar with more of them makes things easier for when you encounter code that use them, taking away some of the initial mystery. See that directory's [README file]() for a description of which libraries are used as well as what alternative versions of the primary script are available.

# References

- General
    - [Analyze (and backup) G Suite images codelab](http://g.co/codelabs/drive-gcs-vision=-sheets)
    - [Google APIs client libraries](https://developers.google.com/api-client-library)
- G Suite
    - [Google Drive API home page](https://developers.google.com/drive)
    - [Google Sheets API home page](https://developers.google.com/sheets)
    - [G Suite developer overview & documentation](https://developers.google.com/gsuite).
- Google Cloud Platform (GCP)
    - [Google Cloud Storage home page](https://cloud.google.com/storage)
    - [Google Cloud Vision home page and live demo](https://cloud.google.com/vision)
        - [Google Cloud Vision API documentation](https://cloud.google.com/vision/docs)
        - [Vision API image labeling docs](https://cloud.google.com/vision/docs/labels)
    - [Python on the Google Cloud Platform](https://cloud.google.com/python)
    - [GCP API documentation](https://cloud.google.com/docs).
    - [GCP product client libraries](https://cloud.google.com/apis/docs/cloud-client-libraries)
