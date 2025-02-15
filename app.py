import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
import cv2
import time

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")
print(SPOTIFY_CLIENT_ID)

# Initialize Spotify authentication
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET,
    redirect_uri=SPOTIFY_REDIRECT_URI,
    scope="user-read-playback-state user-modify-playback-state"
))

# Get your WiiM Amp's Spotify Connect device ID
devices = sp.devices()
wiim_device = None
for device in devices["devices"]:
    if "gianduja" in device["name"].lower():
        wiim_device = device["id"]
        break

if not wiim_device:
    print("WiiM Amp not found in Spotify devices.")
    exit()


def play_song(uri: str):
    sp.start_playback(device_id=wiim_device, uris=[uri])


# Initialize the webcam
cap = cv2.VideoCapture(0)

# Initialize OpenCV QR code detector
detector = cv2.QRCodeDetector()

last_played_song = None
last_played_time = None

while True:
    # Capture frame from webcam
    ret, frame = cap.read()
    if not ret:
        break

    # Detect and decode QR code
    data, bbox, _ = detector.detectAndDecode(frame)

    if bbox is not None:
        bbox = bbox.astype(int)  # Convert bounding box to integer type
        for i in range(len(bbox[0])):  # Iterate over points
            pt1 = tuple(bbox[0][i])  # Convert to tuple
            pt2 = tuple(bbox[0][(i + 1) % len(bbox[0])])  # Next point
            cv2.line(frame, pt1, pt2, (0, 255, 0), 2)

        if data:
            print(f"QR Code Data: {data}")

            if "spotify" in data and (data != last_played_song or time.time() - last_played_time > 10):
                last_played_song = data
                last_played_time = time.time()
                play_song(data)
                print("Playing song on WiiM Amp via Spotify")

    # Display the frame
    cv2.imshow("QR Code Scanner", frame)

    # Exit on pressing 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
