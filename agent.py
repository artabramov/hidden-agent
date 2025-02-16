import argparse
import os
import time
import signal
import sys
import requests
import mimetypes

def _signal_handler(sig, frame):
    print("\nProgram is exiting gracefully...")
    sys.exit(0)

def send_file(hidden_uri, collection_id, user_token, file_path):
    url = f"{hidden_uri}/api/v1/collection/{collection_id}/document"
    headers = {
        "Authorization": f"Bearer {user_token}",
    }

    # Определяем MIME-тип файла
    mime_type, _ = mimetypes.guess_type(file_path)
    if mime_type is None:
        mime_type = 'application/octet-stream'  # Если MIME-тип не найден, используем универсальный тип

    # Создаем данные формы для отправки файла
    with open(file_path, 'rb') as file:
        files = {'file': (os.path.basename(file_path), file, mime_type)}  # Указываем MIME-тип
        response = requests.post(url, headers=headers, files=files)

    if response.status_code == 201:
        print(f"File {file_path} successfully uploaded.")
        return True
    else:
        print(f"Failed to upload file {file_path}. Status code: {response.status_code}")
        print(f"Response content: {response.content}")
        return False

def main():
    # Create argument parser
    parser = argparse.ArgumentParser(description="A program to process data with the specified arguments")

    # Add arguments
    parser.add_argument('--directory_path', type=str, required=True, help='Path to the directory')
    parser.add_argument('--collection_id', type=int, required=True, help='Collection ID')
    parser.add_argument('--user_token', type=str, required=True, help='User token')
    parser.add_argument('--hidden_uri', type=str, required=True, help='Base URI for file upload')

    # Parse arguments
    args = parser.parse_args()

    # Get argument values
    directory_path = args.directory_path
    collection_id = args.collection_id
    user_token = args.user_token
    hidden_uri = args.hidden_uri

    # Print the received values
    print(f"Directory path: {directory_path}")
    print(f"Collection ID: {collection_id}")
    print(f"User token: {user_token}")
    print(f"Hidden URI: {hidden_uri}")

    # Register signal handler for SIGINT (Ctrl+C)
    signal.signal(signal.SIGINT, _signal_handler)

    # Infinite loop to monitor the directory
    while True:
        # Get current files in the directory
        current_files = set(os.listdir(directory_path))

        # Check for new files in the directory
        for file_name in current_files:
            file_path = os.path.join(directory_path, file_name)
            if os.path.isfile(file_path):  # Ensure it's a file, not a subdirectory
                print(f"New file detected: {file_name}")
                
                # Try to send the file
                if send_file(hidden_uri, collection_id, user_token, file_path):
                    # If the upload was successful, delete the file
                    os.remove(file_path)
                    print(f"File {file_name} deleted.")
                else:
                    print(f"File {file_name} not deleted due to upload failure.")

        # Wait for a short period before checking again
        time.sleep(5)

if __name__ == "__main__":
    main()
