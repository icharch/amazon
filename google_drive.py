from dataclasses import dataclass, asdict
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import date
from google.oauth2.credentials import Credentials

@dataclass
class GoogleDriveManager:
    def __init__(self, creds: Credentials):
        self.credentials = creds
        # self.create_spreadsheet()

    def create_spreadsheet(self):
        try:
            service = build('sheets', 'v4', credentials=self.credentials)
            spreadsheet = {
                'properties': {
                'title': "amazon_orders_" + str(date.today())
                }
            }
            spreadsheet = service.spreadsheets().create(body=spreadsheet, fields='spreadsheetId').execute()
            print(f"Spreadsheet ID: {(spreadsheet.get('spreadsheetId'))}")
            # return upload_to_folder(self, folder_id= '1Nye0kB64z7Jt1bdgWbCv6lv_TfdcxurN')
            move_file_to_folder(spreadsheet.get('spreadsheetId'), '1Nye0kB64z7Jt1bdgWbCv6lv_TfdcxurN', self.credentials)
            return spreadsheet.get('spreadsheetId')
        except HttpError as error:
            print(F'An error occurred: {error}')
            return None 


def upload_to_folder(self, folder_id):
    """Upload a file to the specified folder and prints file ID, folder ID
    Args: Id of the folder
    Returns: ID of the file uploaded

    Load pre-authorized user credentials from the environment.
    TODO(developer) - See https://developers.google.com/identity
    for guides on implementing OAuth2 for the application.
    """

    try:
        # create drive api client
        service = build('sheets', 'v4', credentials=self.credentials)

        spreadsheet = {
            'mimeType': 'application/vnd.google-apps.spreadsheet',
            'properties': {
            'title': "YY_amazon_orders_" + str(date.today())
            }
        }

        # pylint: disable=maybe-no-member
        spreadsheet = service.spreadsheets().create(body=spreadsheet,
                                                    fields='spreadsheetId') \
            .execute()

        print(f"Spreadsheet ID: {(spreadsheet.get('spreadsheetId'))}")
        return spreadsheet.get('spreadsheetId')

    except HttpError as error:
        print(F'An error occurred: {error}')
        return None

def move_file_to_folder(file_id, folder_id, creds):
    try:
        service = build('drive', 'v3', credentials=creds)
        file = service.files().get(fileId=file_id, fields='parents').execute()
        previous_parents = ",".join(file.get('parents'))
        file = service.files().update(fileId=file_id, addParents=folder_id,
                                      removeParents=previous_parents,
                                      fields='id, parents').execute()
        return file.get('parents')
    except HttpError as error:
        print(F'An error occurred: {error}')
        return None
