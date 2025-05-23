import requests
import json
import os

# shared album identifier, found in shared album website url
SHARED_STREAM_TOKEN = "B25JtdOXmhS13T"

BASE_62_CHAR_SET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"


def base_62_to_int(base62String):
    """converts a base62 string into an integer"""
    result = 0
    for i in range(len(base62String)):
        result = result * 62 + BASE_62_CHAR_SET.index(base62String[i])

    return result


def extract_server_partition():
    """determines server partition from shared stream token"""
    if SHARED_STREAM_TOKEN[0] == "A":
        return base_62_to_int(SHARED_STREAM_TOKEN[1])

    return base_62_to_int(SHARED_STREAM_TOKEN[1:3])


def get_base_url():
    """constructs the base url of the API from the server partition"""
    server_partition = extract_server_partition()

    return f"p{server_partition:02}-sharedstreams.icloud.com"


def fetch_photos_metadata():
    """fetches metadata for all photos in the shared album"""
    url = f"https://{get_base_url()}/{SHARED_STREAM_TOKEN}/sharedstreams/webstream"

    response = requests.post(url, json={"streamCtag": None})
    response.raise_for_status()

    return response.json()["photos"]


# should be done clientside, as urls provided from this endpoint expire quickly
# response will be a json with keys corresponding to checksums under the given photo's derivative field, and body containing the url to find the picture at

#     url = f"https://{get_base_url()}/{SHARED_STREAM_TOKEN}/sharedstreams/webasseturls"
#     data = {"photoGuids": [photoGuids]} # photo guids array must be either 5 or 25 long
#     response = requests.post(url, data=json.dumps(data))


def get_output_path():
    """returns path to save json data to, depending on environment"""
    return "/data/photos_metadata.json" if os.getenv("PROD") else "photos_metadata.json"


def save_json(file_path, data):
    """saves the given data to a json file"""
    with open(file_path, "w") as f:
        json.dump(data, f)
        f.write("\n")


def main():
    photos_metadata = fetch_photos_metadata()
    output_path = get_output_path()

    save_json(output_path, photos_metadata)


if __name__ == "__main__":
    main()
