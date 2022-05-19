import os.path
from re import sub

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
        folder_ID = ''
        query = f"parents = '{folder_ID}'"
        # call the Drive v3 API
        response = service.files().list(
            fields = "nextPageToken, files(name, id)",
            q = query,
            ).execute()

        #
        folders = response.get("files", [])

        if not folders:
            print("No files found")
            return

        # print(folders)
        print("Folders:")
        # makes a request for each folder inside the Library folder
        for folder in folders:
            print(folder['name'])
            query = f"parents = '{folder['id']}'"

            response = service.files().list(
                q = query,
                fields = "nextPageToken, files(name, parents)"
             ).execute()

            files = response.get('files')
            nextPageToken = response.get('nextPageToken')

            while nextPageToken:
                response = service.files().list(q=query, pageToken = nextPageToken).execute()
                files.extend(response.get(files))
                nextPageToken = response.get("nextPageToken")

            for file in files:
                print(f"\t {file['name']}")
            

    except HttpError as error:
        print(f"An error occured: {error}")

if __name__ == "__main__":
    main()