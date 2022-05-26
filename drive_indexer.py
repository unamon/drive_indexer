import os.path
from re import sub

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.errors import HttpError



SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly', 'https://www.googleapis.com/auth/spreadsheets']

def get_creds():
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
    return creds

def get_books_data():

    creds = get_creds()

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
        print("Creating values...")
        values = [["Title", "Folder"]] # the value list will be populated by the books metadata

        # makes a request for each folder inside the Library folder
        for folder in folders:
            
            query = f"parents = '{folder['id']}'"

            response = service.files().list(
                q = query,
                fields = "nextPageToken, files(name, size, parents, id)"
             ).execute()

            files = response.get('files')
            nextPageToken = response.get('nextPageToken')

            while nextPageToken:
                response = service.files().list(q=query,
                 
                pageToken = nextPageToken).execute()
                files.extend(response.get(files))
                nextPageToken = response.get("nextPageToken")

            for file in files:
                
                file_link = f"=hyperlink(\"https://drive.google.com/file/d/{file['id']}\";\"{file['name']}\")"
                # name = name.replace(".pdf", "").replace("_", " ")
                values.append([file_link, str(folder['name'])])            
        return(values)

    except HttpError as error:
        print(f"An error occured: {error}")

def create_spreadsheet():
    creds = get_creds()
    sheet_ID = ''
    values = get_books_data()
    body = {
        "values":values
    }
    try:
        service = build('sheets', 'v4', credentials=creds)
        result = service.spreadsheets().values().update(
        spreadsheetId=sheet_ID,
        body=body,
        range = "A:B",
        valueInputOption = "USER_ENTERED"
        ).execute()

        print('{0} cells updated.'.format(result.get('updatedCells')))


    except HttpError as error:
        print(f"An error occurred in the sheets:{error}")



if __name__ == "__main__":
    create_spreadsheet()