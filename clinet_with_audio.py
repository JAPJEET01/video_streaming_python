import cv2
import socket
import pyaudio
import threading
from pynput import keyboard

# Server details
server_ip = '127.0.0.1'
server_port_video = 9999
server_port_audio = 9998

# Create socket objects
video_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
audio_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Capture video from webcam
cap = cv2.VideoCapture(0)

# PyAudio configuration for sending audio
p = pyaudio.PyAudio()
send_stream = p.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=512)

# PyAudio configuration for receiving audio
receive_stream = p.open(format=pyaudio.paInt16, channels=1, rate=44100, output=True, frames_per_buffer=512)

# Flag to indicate if 'p' key is pressed
key_pressed = threading.Event()

def on_press(key):
    try:
        if key.char == 'p':
            key_pressed.set()
    except AttributeError:
        pass

def on_release(key):
    if key == keyboard.Key.esc:
        return False
    try:
        if key.char == 'p':
            key_pressed.clear()
    except AttributeError:
        pass

listener = keyboard.Listener(on_press=on_press, on_release=on_release)
listener.start()

def send_video():
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Encode the frame
        _, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
        
        # Send the frame
        video_socket.sendto(buffer, (server_ip, server_port_video))
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    video_socket.close()
    cv2.destroyAllWindows()

def send_audio():
    while True:
        if key_pressed.is_set():
            data = send_stream.read(1024)
            audio_socket.sendto(data, (server_ip, server_port_audio))

def receive_audio():
    while True:
        data, addr = audio_socket.recvfrom(4096)
        receive_stream.write(data)

video_thread = threading.Thread(target=send_video)
send_audio_thread = threading.Thread(target=send_audio)
receive_audio_thread = threading.Thread(target=receive_audio)

video_thread.start()
send_audio_thread.start()
receive_audio_thread.start()

video_thread.join()
send_audio_thread.join()
receive_audio_thread.join()

send_stream.stop_stream()
send_stream.close()
receive_stream.stop_stream()
receive_stream.close()
p.terminate()
audio_socket.close()
