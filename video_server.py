#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
About: Simple video server.
"""

import http.server
import socketserver
import os

SERVICE_IP = "10.0.0.12"
SERVICE_PORT = 8888
VIDEO_DIRECTORY = "videos"  # Directory where video files are stored

class VideoRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        """Serve a GET request."""
        if self.path.startswith("/video"):
            self.serve_video()
        else:
            super().do_GET()

    def serve_video(self):
        """Serve a video file."""
        video_path = self.path.lstrip("/")
        full_path = os.path.join(VIDEO_DIRECTORY, video_path)
        
        if not os.path.isfile(full_path):
            self.send_error(404, "File not found")
            return
        
        self.send_response(200)
        self.send_header("Content-type", "video/mp4")
        self.send_header("Content-Length", str(os.path.getsize(full_path)))
        self.end_headers()
        
        with open(full_path, "rb") as video_file:
            self.wfile.write(video_file.read())

def run():
    """Run the video server."""
    handler = VideoRequestHandler
    httpd = socketserver.TCPServer((SERVICE_IP, SERVICE_PORT), handler)
    print(f"Serving video server at http://{SERVICE_IP}:{SERVICE_PORT}")
    httpd.serve_forever()

if __name__ == "__main__":
    run()