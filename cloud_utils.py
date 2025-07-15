from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

# ✅ Authenticate Google Drive
def authenticate_drive():
    gauth = GoogleAuth()

    # These lines will automatically try to load saved credentials
    gauth.LoadCredentialsFile("mycreds.txt")
    if gauth.credentials is None:
        # Authenticate if they're not there
        gauth.LocalWebserverAuth()
    elif gauth.access_token_expired:
        # Refresh them if expired
        gauth.Refresh()
    else:
        # Initialize the saved creds
        gauth.Authorize()

    # Save the current credentials to a file
    gauth.SaveCredentialsFile("mycreds.txt")

    drive = GoogleDrive(gauth)
    return drive

# ✅ Upload notes.json to Google Drive
def upload_notes(drive):
    # Check if file already exists
    file_list = drive.ListFile({'q': "title='notes.json' and trashed=false"}).GetList()
    if file_list:
        file = file_list[0]
        file.SetContentFile('notes.json')
        file.Upload()
        print("Updated notes.json on Google Drive!")
    else:
        file = drive.CreateFile({'title': 'notes.json'})
        file.SetContentFile('notes.json')
        file.Upload()
        print("Uploaded notes.json to Google Drive!")

# ✅ Download notes.json from Google Drive
def download_notes(drive):
    file_list = drive.ListFile({'q': "title='notes.json' and trashed=false"}).GetList()
    if file_list:
        file = file_list[0]
        file.GetContentFile('notes.json')
        print("Downloaded notes.json from Google Drive!")
    else:
        print("notes.json not found on Google Drive.")
