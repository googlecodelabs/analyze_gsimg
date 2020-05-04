# Alternative Python versions

You may find wildly varying code when it comes to security when see code in our docs, blog posts, repos, and work software. The alternatives here attempt to address differences and show the options of libraries & authorization schemes so users can select the one they're most familiar with, or learn about something else they _should_ be using. **Caveat:** the files here may not as regularly maintained as the primary codelab files.

There are several generations of Google-related authorization and client libraries for Python—other languages may also have this issue. Google upgraded to a newer authorization library (see below) in [May 2017](https://github.com/googleapis/oauth2client/pull/714), but plenty of code using the older auth libraries is still out there, so some of the files here are also meant to help with the migration process.


> **Authentication vs. Authorization**:
> So, *Authentication* is all about identities and establishing "you are who you say you are." Examples include logins & passwords, 2FA, biometrics (handprint, retina scan), HTTP Basic & Digest, etc. *Authorization* is all about data access *after* authentication complete. Yes, you are who you say you are, but do you have access to the data you're requesting?
>
> Both terms are generally referred to in industry as "authn" & "authz" for differentiation. Another source of confusion is that as a whole, the general term "auth" is used to describe both, especially when used in conjunction with each other.


## What libraries are available

* Older auth libraries
    - \*[`httplib2`](https://github.com/httplib2/httplib2)
    - [`oauth2client`](https://github.com/googleapis/oauth2client)

While `oauth2client` is Python 2 & 3 compatible, cache OAuth tokens for developers, and threadsafe, it's unfortunately deprecated and no longer actively developed nor maintained. (\* — `httplib2` is still used internally by the newer auth libraries below, but users no longer have to do so explicitly.) So we recommend you port to these newer auth libraries:

* Newer auth libraries
    - [`google.auth` & `google.oauth2`](https://github.com/googleapis/google-auth-library-python)
    - [`google_auth_oauthlib`](https://github.com/googleapis/google-auth-library-python-oauthlib)

These libraries are available for both Python 2 & 3 and are currently maintained, however they require developers to manage their own OAuth tokens. In our code samples, you'll see that the OAuth2 credentials are saved as JSON (to `tokens.json`). The only issue with the token management service is that it's not threadsafe (whereas it is in the older libraries that manage the tokens on behalf of developers).

If threadsafety isn't a concern in your applications, we encourage you to move to the newer, supported auth libraries instead and encourage developers to compare [final/analyze_gsimg.py](/final/analyze_gsimg.py) with [alt/analyze_gsimg-newauth.py](/alt/analyze_gsimg-newauth.py) to know the diffs and recommend you review the section below called "Migrating to newer auth libs" and get migration tips there. Using `diff -u` (or `-c`) should show you the *exact* diffs.

* GCP (higher-level) product client libraries

"Google Cloud client libraries" or "GCP client libraries" both refer to *product* client libraries, meaning GCP products (Cloud Storage, Cloud Vision, etc.) have their own client libraries. If you're only developing using GCP tools, stick with these as they're the newest, best-perfoming, and are the recommended tools to use.

However, most *non-Cloud* Google APIs (G Suite, Maps, Analytics, YouTube, etc.), generally use (the older) Google APIs *platform* client libraries (that support multiple products, as no product client libraries typically exist for these APIs.) A platform client library can be seen as a "lowest common denominator" that can let you talk across all Google APIs, including GCP APIs.

This codelab involved both GCP & G Suite APIs, so we employed the platform client library (for Python) for the purposes of consistency and code readability. However, we recommend porting Cloud Storage and Cloud Vision usage to their respective product client libraries, and you'd definitely do so for apps in production. Compare [final/analyze_gsimg.py](/final/analyze_gsimg.py) with [alt/analyze_gsimg-oldauth-gcp.py](/alt/analyze_gsimg-oldauth-gcp.py) and get migration tips. Using `diff -u` (or `-c`) should show you the *exact* diffs.


## Service account authorization

- G Suite APIs: used primarily to access (human) user data, such as documents, email messages, etc., so *user account authorization* ("usr acct authz") is mainly used as those users whom the data belongs to must consent to access to their data by your application. When creating credentials in the Cloud Console, select "OAuth client ID".
- GCP APIs: the GCP world is different... data here is generally owned by an application (a project) or a robot user, so *service account authorization* ("svc acct authz") is standard for GCP APIs. When creating credentials in the Cloud Console, select "Service account".

This tutorial's sample app uses both G Suite *and* GCP APIs, so do we use user or service account authz? The answer is you can use either, but we picked user auth because the premise is a corporate user that has too many images in their Google Drive folder. Those images can be archived to Cloud Storage and sent to Cloud Vision for analysis. The results are written to that user's Google Sheets spreadsheet.

To get this app to work with service accounts, you need to give that service account access to read that user's image files and write permission to the spreadsheet by adding the service account email address to those files. Then switch the app from usr acct authz to svc acct authz, and things will work the same. Compare [final/analyze_gsimg.py](/final/analyze_gsimg.py) with [alt/analyze_gsimg-oldauth-svc.py](/alt/analyze_gsimg-oldauth-svc.py) and get migration tips. Using `diff -u` (or `-c`) should show you the *exact* diffs.

There are additional svc acct authz versions in `alt`. All of them have `-svc` in their filenames, and you'll find them shorter than their user account counterparts because there's no longer a need for code that manages user tokens.


## Alternatives and descriptions

Filename | Description
--- | ---
`final/analyze_gsimg.py` | The primary sample; uses the older auth libraries and platform client libraries
`alt/analyze_gsimg-newauth.py` | Same as `final/analyze_gsimg.py` but uses the newer auth libraries
`alt/analyze_gsimg-oldauth-gcp.py` | Same as `final/analyze_gsimg.py` but uses the GCP product client libraries
`alt/analyze_gsimg-newauth-gcp.py` | Same as `alt/analyze_gsimg-newauth.py` but uses the GCP product client libraries
`alt/analyze_gsimg-oldauth-svc.py` | Same as `final/analyze_gsimg.py` but uses svc acct auth instead of user auth
`alt/analyze_gsimg-newauth-svc.py` | Same as `alt/analyze_gsimg-newauth.py` but uses svc acct auth instead of user auth
`alt/analyze_gsimg-oldauth-svc-gcp.py` | Same as `alt/analyze_gsimg-oldauth-svc.py` but uses the GCP product client libraries and same as `alt/analyze_gsimg-oldauth-gcp.py` but uses svc acct auth instead of user auth
`alt/analyze_gsimg-newauth-svc-gcp.py` | Same as `alt/analyze_gsimg-oldauth-svc-gcp.py` but uses the newer auth libraries

The code structure, variable names, and even the comments b/w all of them are *identical* save for their use of the various libraries described, meaning a `diff` between any pair will highlight only the *exact* differences that are meaningful, ultimately letting you gain insight on porting/migrating b/w them.

### Migrating to newer auth libs

If you wish to migrate from the older to current/newer auth libs, the basic steps are outlined below. This is useful for those who have existing code on the older auth libs or find older code online.

Replace...

    from httplib2 import Http
    from oauth2client import file, client, tools

...with...

    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from google.oauth2 import credentials

Replace...

    store = file.Storage('storage.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('client_secret.json', SCOPES)
        creds = tools.run_flow(flow, store)

...with... (be sure to also define `TOKENS = 'tokens.json'` above)

    if os.path.exists(TOKENS):
        creds = credentials.Credentials.from_authorized_user_file(TOKENS)
    if not (creds and creds.valid):
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                    'client_secret.json', SCOPES)
            creds = flow.run_local_server()
        with open(TOKENS, 'w') as token:
            token.write(creds.to_json())

Replace...

    HTTP = creds.authorize(Http())
    DRIVE  = discovery.build('drive',   'v3', http=HTTP)
    GCS    = discovery.build('storage', 'v1', http=HTTP)
    VISION = discovery.build('vision',  'v1', http=HTTP)
    SHEETS = discovery.build('sheets',  'v4', http=HTTP)

...with...

    DRIVE  = discovery.build('drive',   'v3', credentials=creds)
    GCS    = discovery.build('storage', 'v1', credentials=creds)
    VISION = discovery.build('vision',  'v1', credentials=creds)
    SHEETS = discovery.build('sheets',  'v4', credentials=creds)

### Migrating to service account authorization

If you're more likely to engage with G Suite documents from a service account along with standard GCP usage, it makes sense to migrate from user account to service account authorization. The largest change is to completely remove the management of user account auth OAuth2 tokens.

Replace...

    from google.auth.transport.requests import Request
    from google_auth_oauthlib.flow import InstalledAppFlow

...with...

    import google.auth

Replace...

    creds = None
    TOKENS = 'tokens.json' # OAuth2 token storage
    SCOPES = (
        'https://www.googleapis.com/auth/drive.readonly',
        'https://www.googleapis.com/auth/devstorage.full_control',
        'https://www.googleapis.com/auth/cloud-vision',
        'https://www.googleapis.com/auth/spreadsheets',
    )
    if os.path.exists(TOKENS):
        creds = credentials.Credentials.from_authorized_user_file(TOKENS)
    if not (creds and creds.valid):
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                    'client_secret.json', SCOPES)
            creds = flow.run_local_server()
        with open(TOKENS, 'w') as token:
            token.write(creds.to_json())

...with...

    creds, _proj_id = google.auth.default()
