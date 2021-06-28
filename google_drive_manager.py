from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import secrets


class GoogleDriveManager:
    def __init__(self):
        google_auth = GoogleAuth()
        google_auth.LocalWebserverAuth()  # client_secrets.json need to be in the same directory as the script
        self.drive = GoogleDrive(google_auth)

    def view_files(self):
        # View all folders and file in your Google Drive
        file_list = self.drive.ListFile({'q': "'root' in parents and trashed=false"}).GetList()
        for file in file_list:
            print('Title: %s, ID: %s' % (file['title'], file['id']))
            # Get the folder ID that you want
            if file['title'] == "To Share":
                file_id = file['id']

    def download_random_picture(self, name):
        file_list = self.drive.ListFile({'q': "'root' in parents and trashed=false"}).GetList()
        pictures_id = None
        for file in file_list:
            if file['title'] == "Pictures":
                pictures_id = file['id']
        file_list = self.drive.ListFile({'q': f"'{pictures_id}' in parents and trashed=false"}).GetList()
        number = secrets.randbelow(len(file_list))
        file_list[number].GetContentFile(name)

# Образец применения
# @bot.message_handler(commands=["send_random_picture_from_drive"])
# def send_random_picture_from_drive_command(message):
#     name = "temp_picture.jpg"
#     gd_manager.download_random_picture(name)
#     if os.path.isfile(name):
#         with open(name, "rb") as file:
#             bot.send_photo(message.chat.id, file)
#         os.remove(name)
#     else:
#         bot.send_message(message.chat.id, "При отправке фото произошла ошибка!")
