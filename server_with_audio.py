# import cv2
# import socket
# import numpy as np
# import pyaudio
# import threading

# # Server details
# server_ip = '0.0.0.0'
# server_port_video = 9999
# server_port_audio = 9998

# # Create a socket object for video
# video_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# video_socket.bind((server_ip, server_port_video))

# # Create a socket object for audio
# audio_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# audio_socket.bind((server_ip, server_port_audio))

# print("Server listening on ports:", server_port_video, server_port_audio)

# # Dictionary to hold frames and audio for each client
# client_data = {}

# # PyAudio configuration
# p = pyaudio.PyAudio()
# audio_stream = p.open(format=pyaudio.paInt16, channels=1, rate=44100, output=True, frames_per_buffer=512)

# def handle_video():
#     while True:
#         data, addr = video_socket.recvfrom(65536)
#         np_data = np.frombuffer(data, dtype=np.uint8)
#         frame = cv2.imdecode(np_data, cv2.IMREAD_COLOR)
        
#         if frame is not None:
#             if addr not in client_data:
#                 client_data[addr] = {'frame': None, 'audio': None}
#             client_data[addr]['frame'] = frame
        
#         for client_addr, client_info in client_data.items():
#             if client_info['frame'] is not None:
#                 window_name = f'Client {client_addr} - Video'
#                 cv2.imshow(window_name, client_info['frame'])
        
#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             break

# def handle_audio():
#     while True:
#         data, addr = audio_socket.recvfrom(4096)
#         if addr not in client_data:
#             client_data[addr] = {'frame': None, 'audio': None}
#         client_data[addr]['audio'] = data
        
#         # Play the audio data
#         audio_stream.write(data)

# video_thread = threading.Thread(target=handle_video)
# audio_thread = threading.Thread(target=handle_audio)

# video_thread.start()
# audio_thread.start()

# video_thread.join()
# audio_thread.join()

# video_socket.close()
# audio_socket.close()
# cv2.destroyAllWindows()
# audio_stream.stop_stream()
# audio_stream.close()
# p.terminate()



import cv2
import socket
import numpy as np
import pyaudio
import threading

# Server details
server_ip = '0.0.0.0'
server_port_video = 9999
server_port_audio = 9998

# Create a socket object for video
video_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
video_socket.bind((server_ip, server_port_video))

# Create a socket object for audio
audio_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
audio_socket.bind((server_ip, server_port_audio))

print("Server listening on ports:", server_port_video, server_port_audio)

# Dictionary to hold frames and audio for each client
client_data = {}
# List to hold the addresses of connected clients
client_addresses = set()

# PyAudio configuration
p = pyaudio.PyAudio()
audio_stream = p.open(format=pyaudio.paInt16, channels=1, rate=44100, output=True, frames_per_buffer=512)

def handle_video():
    while True:
        data, addr = video_socket.recvfrom(65536)
        np_data = np.frombuffer(data, dtype=np.uint8)
        frame = cv2.imdecode(np_data, cv2.IMREAD_COLOR)
        
        if frame is not None:
            if addr not in client_data:
                client_data[addr] = {'frame': None, 'audio': None}
            client_data[addr]['frame'] = frame
        
        for client_addr, client_info in client_data.items():
            if client_info['frame'] is not None:
                window_name = f'Client {client_addr} - Video'
                cv2.imshow(window_name, client_info['frame'])
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

def handle_audio():
    while True:
        data, addr = audio_socket.recvfrom(4096)
        if addr not in client_data:
            client_data[addr] = {'frame': None, 'audio': None}
            client_addresses.add(addr)
        client_data[addr]['audio'] = data
        
        # Play the audio data
        audio_stream.write(data)
        
        # Broadcast the audio data to all other clients
        for client_addr in client_addresses:
            if client_addr != addr:
                audio_socket.sendto(data, client_addr)

video_thread = threading.Thread(target=handle_video)
audio_thread = threading.Thread(target=handle_audio)

video_thread.start()
audio_thread.start()

video_thread.join()
audio_thread.join()

video_socket.close()
audio_socket.close()
cv2.destroyAllWindows()
audio_stream.stop_stream()
audio_stream.close()
p.terminate()
