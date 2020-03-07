# Alternative Python versions

There are various client libraries offered by Google. What's in the documentation may use a different library than what you've seen elsewhere. The alternatives in this folder attempt to address this so users can select the one they're most comfortable with or prefer. The caveat is those found here may not be maintained as regularly as the others that are used as part of the codelab.

## Mainly a Python issue

There are several generations of Google-related authorization and client libraries in the wild for Python (other languages may also have this issue). I will also try to describe what's below in a future blog post, but being transparent with developers is the responsible thing to do.

## What authorization libraries are available

* Older auth libraries
    - [`httplib2`](https://github.com/httplib2/httplib2)
    - [`oauth2client`](https://github.com/googleapis/oauth2client)

These libraries are Python 2 and 3 compatible, cache the OAuth tokens for users (developers), and are threadsafe. Unfortunately, they both have been deprecated and are no longer actively developed nor maintained. They're primarily used for Google APIs in which *user authorization* is required (meaning the data behind the API belongs to a user who must consent to access by your code). (It is different from *service account authorization* where the data belongs to an application or cloud-based service.)

* Newer auth libraries
    - [`google.auth`](https://github.com/googleapis/google-auth-library-python)
    - [`google_auth_oauthlib`](https://github.com/googleapis/google-auth-library-python-oauthlib)

These libraries are available for both Python 2 & 3 and are currently maintained, however they require the users (developers) to manage their own OAuth tokens. In our code samples, we use the `pickle` module to serialize the OAuth2 credentials (because JSON isn't serializable). Unfortunately, the `pickle` protocols between Python 2 and 3 are not compatible, meaning your applications cannot use the credentials that were written with the other Python interpreter. Essentially you must be Python 3 all the way (or Python 2) and can't switch between the two without deleting the pickle file and reauthorizing each time you switch Python generations. Note the auth token storage code here isn't threadsafe.

* GCP (higher-level) product client libraries

Both auth libraries mentioned above focus on providing lower-level access across multiple of Google APIs. If you are *only* using Google Cloud Platform (GCP) APIs, the recommended approach is to use the GCP higher-level client libraries but are product-focused, meaning a client library for Google Cloud Storage, another one for Google Cloud Vision, etc. These higher-level libraries use the "newer auth libraries" above and default to service account authorization but will fallback to user auth if needed.

In this codelab, because we only use two GCP APIs (Google Cloud Storage and Cloud Vision API), only client libraries for these are available. In the alternative versions below using these client libraries, access to the G Suite APIs (Drive and Sheets) will continue to use the broader, lower-level auth libraries above.

## Authorization libraries for codelab sample

For this codelab sample, we've selected to use the older auth libraries for greater compatibility across Python 2 and 3 users as well as for automated management of OAuth2 tokens, providing a less complex user experience. In the event these libraries become totally obsoleted/unsupported when accessing Google APIs, we've provided several alternative versions of the final application script below.

## Alternatives and descriptions

- `analyze_gsimg-newauth.py` — Same as `final/analyze_gsimg.py` but uses the newer auth libraries
- `analyze_gsimg-oldauth-gcp.py` — Same as `final/analyze_gsimg.py` but uses the GCP product client libraries
- `analyze_gsimg-newauth-gcp.py` — Same as `alt/analyze_gsimg-newauth.py` but uses the GCP product client libraries

Filename | Description
--- | ---
`final/analyze_gsimg.py` | The primary sample; uses the older auth libraries
`alt/analyze_gsimg-newauth.py` | Same as `final/analyze_gsimg.py` but uses the newer auth libraries
- `alt/analyze_gsimg-oldauth-gcp.py` | Same as `final/analyze_gsimg.py` but uses the GCP product client libraries
- `alt/analyze_gsimg-newauth-gcp.py` | Same as `alt/analyze_gsimg-newauth.py` but uses the GCP product client libraries

The code structure, variable names, and even the comments b/w all of them are *identical* save for their use of the various libraries described, meaning a `diff` between any pair will highlight only the *exact* differences that are meaningful, ultimately letting you gain insight on porting/migrating b/w them.

## Further study

GCP auth page
Google APIs auth page


### Backporting

Replace...
    from google.auth.transport.requests import Request
    from google_auth_oauthlib.flow import InstalledAppFlow

...with...
    from httplib2 import Http
    from oauth2client import file, client, tools

Replace...
    if os.path.exists(TOKENS):
        with open(TOKENS, 'r') as f:
            tokens = pickle.load(f)
    if not (tokens and tokens.valid):
        if tokens and tokens.expired and tokens.refresh_token:
            tokens.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                    'client_secret.pickle', SCOPES)
            tokens = flow.run_local_server()
        with open(TOKENS, 'w') as f:
            pickle.dump(tokens, f)

...with...
    store = file.Storage('storage.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('client_secret.json', SCOPES)
        creds = tools.run_flow(flow, store)

Replace...
    DRIVE  = discovery.build('drive',   'v3', credentials=tokens)
    GCS    = discovery.build('storage', 'v1', credentials=tokens)
    VISION = discovery.build('vision',  'v1', credentials=tokens)
    SHEETS = discovery.build('sheets',  'v4', credentials=tokens)

...with...
    HTTP = creds.authorize(Http())
    DRIVE  = discovery.build('drive',   'v3', http=HTTP)
    GCS    = discovery.build('storage', 'v1', http=HTTP)
    VISION = discovery.build('vision',  'v1', http=HTTP)
    SHEETS = discovery.build('sheets',  'v4', http=HTTP)

