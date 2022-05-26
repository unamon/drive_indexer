# Drive Indexer

This scrubs the subfolders of a given folder and lists all the files in them, uploading said list to a given google sheet.

The current version works if I hack it by downloading a folder and reuploading, otherwise it seems that the GDrive api isn't able to see every file in every folder, only every file that I personally opened/downloaded/own?

## How to use

You need the credentials for a project with both the Google Drive API and the Google Spreadsheets API enabled. Download credentials and rename them to "credentials.json", and put in the project folder. You need to authorize the email you use in the API panel as well, or it won't let you use it. 
Do both of these things at https://console.cloud.google.com/home/
