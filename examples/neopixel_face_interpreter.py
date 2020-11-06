import socket as sk
import sys
import time
import board
import neopixel
from InfiniteTimer import InfiniteTimer as infitimer
import threading

PORT = 1986
DELAY = 0.5

pixel_pin = board.D18
num_pixels = 95
ORDER = neopixel.GRB
pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=0.2, auto_write=False, pixel_order=ORDER)

basic_face = [1, 2, 7, 8, 25, 26, 31, 32, 37, 38, 43, 44, 73, 80, 86, 87, 88, 89, 90, 91]

happy_face_1 = [1, 8, 12, 14, 19, 21, 23, 27, 30, 34, 74, 79, 87, 88, 89, 90]
happy_face_2 = [1, 8, 12, 14, 19, 21, 23, 27, 30, 34, 61, 68, 74, 79, 87, 88, 89, 90]

sad_face_1 = [11, 15, 18, 22, 24, 26, 31, 33, 37, 44, 62, 63, 64, 65, 66, 67, 73, 80, 84, 93]
sad_face_2 = [11, 15, 18, 22, 24, 26, 31, 33, 37, 44, 49, 56, 62, 63, 64, 65, 66, 67, 73, 80, 84, 93]
sad_face_3 = [11, 15, 18, 22, 24, 26, 31, 33, 37, 44, 61, 62, 63, 64, 65, 66, 67, 68, 73, 80, 84, 93]

disappointed_face_1 = [0, 3, 6, 9, 13, 14, 19, 20, 37, 38, 43, 44, 49, 50, 55, 56, 76, 77, 87, 90]
disappointed_face_2 = [0, 3, 6, 9, 13, 14, 19, 20, 37, 38, 43, 44, 49, 50, 55, 56, 76, 77, 86, 87, 90, 91]

angry_face_1 = [1, 8, 14, 19, 27, 30, 50, 51, 54, 55, 62, 63, 66, 67, 87, 88, 89, 90]
angry_face_2 = [26, 27, 30, 31, 50, 51, 54, 55, 62, 63, 66, 67, 87, 88, 89, 90]

surprised_face_1 = [2, 7, 13, 20, 24, 26, 27, 30, 31, 33, 38, 39, 42, 43, 63, 64, 65, 66, 75, 78, 87, 88, 89, 90]
surprised_face_2 = [2, 7, 13, 20, 24, 26, 27, 30, 31, 33, 38, 39, 42, 43, 76, 77]

surrendered_face_1 = [0, 1, 2, 3, 6, 7, 8, 9, 26, 27, 30, 31, 38, 39, 42, 43, 75, 76, 77, 78, 86, 91]
surrendered_face_2 = [0, 1, 2, 3, 6, 7, 8, 9, 26, 27, 30, 31, 38, 39, 42, 43, 75, 76, 77, 78]

music_face = [3, 4, 5, 6, 7, 8, 13, 18, 27, 32, 37, 42, 51, 56, 61, 62, 63, 66, 67, 68, 73, 74, 75, 78, 79, 80, 85, 86, 86, 87, 90, 91, 92]

emotion_to_faces = {
    0: [angry_face_1, angry_face_2],
    1: [disappointed_face_1, disappointed_face_2],
    2: [surprised_face_1, surprised_face_2],
    3: [happy_face_1, happy_face_2],
    4: [basic_face],
    5: [sad_face_1, sad_face_2, sad_face_3],
    6: [surrendered_face_1, surrendered_face_2],
    7: [music_face]
}

emotion_to_color = {
    0: (255, 0, 0),
    1: (0, 94, 161),
    2: (89, 38, 128),
    3: (0, 182, 73),
    4: (50, 50, 50),
    5: (0, 64, 191),
    6: (0, 108, 147),
    7: (50, 50, 50)
}

def print_emotion(arguments):
    global order
    emotion = arguments[0]
    color = arguments[1]
    faces = arguments[2]

    if not 0 <= emotion < 8:
        emotion = 4

    face = faces[order % len(faces)]

    for i in face:
        pixels[i] = color
    pixels.show()
    pixels.fill((0, 0, 0))
    order = (order + 1) % 100


server_socket = sk.socket(sk.AF_INET, sk.SOCK_STREAM)
server_socket.setsockopt(sk.SOL_SOCKET, sk.SO_REUSEADDR, 1)

server_socket.bind(("", PORT))

server_socket.listen(1)

client_socket, addr = server_socket.accept()

print('Connected by ', addr)

last_emotion = 4
emotion = 4
color = emotion_to_color[emotion]
faces = emotion_to_faces[emotion]
order = 1

timer = infitimer(DELAY, print_emotion, (emotion, color, faces))
timer.start()

while True:

    data = client_socket.recv(1024)
    if not data:
        break

    emotion = int(data.decode())

    if last_emotion != emotion:
        timer.cancel()
        last_emotion = emotion
        color = emotion_to_color[emotion]
        faces = emotion_to_faces[emotion]
        timer = infitimer(DELAY, print_emotion, (emotion, color, faces))
        timer.start()

    print(emotion)


client_socket.close()
server_socket.close()
