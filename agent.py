"""
This module provides a program that scans a specified directory for
files, uploads them to a server, and deletes them upon successful
upload. The program runs continuously in an infinite loop, scanning
the directory at regular intervals specified by the user. The program
interacts with a REST API to upload files and uses a JWT token for
user authentication.
"""

import argparse
import os
import time
import signal
import sys
import requests
import mimetypes
import types

DEFAULT_HOST = "http://localhost"
DEFAULT_SLEEP = 5
DEFAULT_MIMETYPE = "application/octet-stream"
REQUEST_URI = "{}/api/v1/collection/{}/document"


def main():
    """
    This function serves as the entry point of the program, where it
    processes command-line arguments for a file scanning and upload
    operation. It continuously scans a specified directory for files, 
    uploads them to a server, and deletes them upon successful upload.
    The program is designed to run in an infinite loop, with a pause
    between each scan iteration as specified by the user. It also
    handles termination signals gracefully, ensuring a clean exit
    when interrupted.
    """
    parser = argparse.ArgumentParser(description="\
        A program that scans a specified directory for files, uploads \
        them to a server, and deletes them upon successful upload. It \
        allows you to configure the directory path, collection ID, \
        user token, server URI, and scan interval through command-line \
        arguments. The program runs continuously, with a pause between \
        each scan, and can be terminated gracefully using a termination \
        signal.")
    signal.signal(signal.SIGINT, _exit)

    parser.add_argument("--user_token", type=str, required=True, help="JWT token required for user authentication. This token can be obtained from the application for accessing secured resources.")
    parser.add_argument('--host', type=str, required=False, default=DEFAULT_HOST, help='Base URI for file upload')
    parser.add_argument('--path', type=str, required=True, help='Path to the directory')
    parser.add_argument('--collection_id', type=int, required=True, help='Collection ID')
    parser.add_argument('--sleep', type=int, required=False, default=DEFAULT_SLEEP, help='Pause between scan iterations')

    args = parser.parse_args()
    path = args.path
    collection_id = args.collection_id
    user_token = args.user_token
    host = args.host
    sleep = args.sleep

    print(f"Scanning path: {path}")

    while True:
        current_files = set(os.listdir(path))

        for file_name in current_files:
            file_path = os.path.join(path, file_name)
            if os.path.isfile(file_path):
                if _send_file(host, collection_id, user_token, file_path):
                    os.remove(file_path)
                    print("Deleted: {}".format(file_name))
                else:
                    print("Deletion failed: {}".format(file_name))

        time.sleep(sleep)


def _exit(sig: int, frame: types.FrameType = None):
    """
    This function handles the termination signal, performs any necessary
    cleanup, and then exits the program with a status code of 0. It is
    triggered when the program receives a termination signal, and the
    provided frame is the current stack frame at the time of signal
    reception.
    """
    print("\nExit.")
    sys.exit(0)


def _guess_mimetype(file_path: str):
    """
    This function attempts to guess the MIME type of a file based on its
    file extension. If the MIME type cannot be determined, it returns a
    default MIME type.
    """
    mimetype, _ = mimetypes.guess_type(file_path)
    if mimetype is None:
        mimetype = DEFAULT_MIMETYPE
    return mimetype


def _send_file(host, collection_id, user_token, file_path):
    """
    This function uploads a file to a specified server by sending it via
    an HTTP POST request. It guesses the MIME type of the file, attaches
    the file to the request, and includes an authorization token in the
    request header. If the file upload is successful (status code 201), 
    it prints a success message; otherwise, it prints a failure message
    with the status code and response content.
    """
    with open(file_path, 'rb') as file:
        mimetype = _guess_mimetype(file_path)
        files = { "file": (os.path.basename(file_path), file, mimetype) }

        response = requests.post(
            REQUEST_URI.format(host, collection_id),
            headers={ "Authorization": "Bearer {}".format(user_token) },
            files=files
        )

    if response.status_code == 201:
        print("Uploaded: {}".format(file_path))
        return True

    else:
        print("Upload failed: {}. Code: {}. Response: {}".format(
            file_path, response.status_code, response.content))
        return False


if __name__ == "__main__":
    main()
