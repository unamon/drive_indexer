import os.path

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.errors import HttpError



SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly']


def main():
    creds = None
    # Access and refresh tokens are stored in the file token.json. 
    # It is created automatically when auth flow completes for the first time 
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    #if there are no (valid) credentials available, the user logs in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        # save credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())


    try: 
        service = build("drive", "v3", credentials=creds)

        # call the Drive v3 API
        results = service.files().list(
            fields = "files(name, id)",
            q = "'1wMZ113PdBJnXxpjrDmu4o7dyoR77-meT' in parents",
            ).execute()
        items = results.get("files", [])

        if not items:
            print("No files found")
            return
        
        print("Files:")
        for item in items:
            print(item)

    except HttpError as error:
        print(f"An error occured: {error}")

if __name__ == "__main__":
    main()