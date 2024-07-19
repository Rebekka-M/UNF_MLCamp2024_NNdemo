import io
import os

from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload

import torch

SCOPES = ["https://www.googleapis.com/auth/drive"]
MODEL_FOLDER = "1Xt_Igk67jqUD7Esa5HhuZZFDkYNyoeAT"

class DriveWrapper:
    """Wrapper class for Google Drive API"""
    
    def __init__(self) -> None:
        """Initializes the DriveWrapper class and log-in to Google Drive API"""
        self.creds = None

        # If token already exists, load it
        if os.path.exists("token.json"):
            # Load credentials from file
            self.creds = Credentials.from_authorized_user_file("token.json", SCOPES)
        
        # If there are no (valid) credentials available, let the user log in.
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json", SCOPES
                )
                self.creds = flow.run_local_server(port=0)
                # Save the credentials for the next run
                with open("token.json", "w") as token:
                    token.write(self.creds.to_json())
        
    def load_models(self) -> None:
        """loads models from the folder in Google Drive"""

        # delete all files that are in the models folder
        for file in os.listdir("models"):
            os.remove(f"models/{file}")

        # create drive api client
        service = build("drive", "v3", credentials=self.creds)

        # get list of files in the folder
        try:
            results = (
                service.files()
                .list(
                    q=f"'{MODEL_FOLDER}' in parents and trashed=false", fields="files(id, name)",
                    includeItemsFromAllDrives=True,
                    supportsAllDrives=True,
                ).execute()
            )
        except HttpError as error:
            print(f"An error occurred: {error}")
            results = None
        items = results.get("files", [])

        print(f"Found {len(items)} models in the folder.")

        # download each file
        for item in items:
            try:
                file_id = item["id"]
                request = service.files().get_media(
                    fileId=file_id,
                    supportsAllDrives=True,
                )
                file = io.BytesIO()
                downloader = MediaIoBaseDownload(file, request)
                done = False
                while done is False:
                    status, done = downloader.next_chunk()
                    print(f"Download {int(status.progress() * 100)}.")

                # Save file locally
                with open(f"models/{item['name']}", "wb") as f:
                    f.write(file.getvalue())

            except HttpError as error:
                print(f"An error occurred: {error}")
        
        
        

if __name__ == '__main__':
    dw = DriveWrapper()
    models = dw.load_models()
    print(models)