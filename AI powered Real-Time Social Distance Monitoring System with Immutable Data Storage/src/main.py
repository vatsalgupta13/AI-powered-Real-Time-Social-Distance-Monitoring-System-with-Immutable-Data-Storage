import os
import sys
import cv2 # for loading images and video
import numpy as np
import threading # used to run multiple threads (function calls) at the same time
import imutils # convenience functions to make basic image processing functions such as rotation, resizing
import time
import warnings
import argparse # parser for command line options, arguments and sub commands
from detector import Detector # social distancing tracker
from imutils.video import VideoStream # to stream the video real-time
from flask import Flask, Response, url_for, redirect, render_template # for creating api
from yolo_config import min_conf, min_distance # contains default configurations for yolo
from web3 import Web3 # python library to interact with ethereum blockchain
warnings.filterwarnings("ignore")

vs = None
outputFrame = None
lock = threading.Lock()
web3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
location = ""

app = Flask(__name__)


@app.route("/")
def index():
    return redirect(url_for("social_distancing_tracker"))

# set min confidence real-time
@app.route("/set_confidence/<confidence>", methods=['POST'])
def set_confidence(confidence):
    min_conf[0] = float(confidence)
    print("set confidence: " + str(confidence))
    return Response(status = 200)

#set min distance real time
@app.route("/set_min_distance/<distance>", methods=['POST'])
def set_min_distance(distance):
    min_distance[0] = float(distance)
    print("set distance: " + str(distance))
    return Response(status = 200)


@app.route("/get_location", methods=['GET'])
def get_location():
    return location


@app.route("/get_min_distance", methods=['GET'])
def get_min_distance():
    return str(min_distance[0])


@app.route("/social_distancing_tracker")
def social_distancing_tracker():
    return render_template("socialDistancingTracker.html")


@app.route("/video_feed")
def video_feed():
    return Response(generate(), mimetype="multipart/x-mixed-replace; boundary=frame")


def update_video(detector, frame_rate):
    global vs, outputFrame, lock
    
    frame_counter = 0
    prev = 0

    while True:
        time_elapsed = time.time() - prev
        if time_elapsed > 1./frame_rate:
            prev = time.time()

            frame_counter += 1
            if frame_counter >= int(vs.get(cv2.CAP_PROP_FRAME_COUNT)) - 10:
                frame_counter = 0 
                vs.set(cv2.CAP_PROP_POS_FRAMES, 0)

            (grabbed, frame, violate) = detector.detect_violations()
            if not grabbed:
                break

            with lock:
                outputFrame = frame.copy()

# generate output video
def generate():
    global outputFrame, lock
    
    while True:
        with lock:
            if outputFrame is None:
                continue
            (flag, encodedImage) = cv2.imencode(".jpg", outputFrame)
            if not flag:
                continue
        yield b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray(encodedImage) + b'\r\n'

# update video
def parse_args():
    """
    Get arguments to run detection model. Input video file to detect social distancing, or
    by default, use webcam for detection.
    :return: program arguments
    """
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--input", type=str, default="",
                    help="path to (optional) input video file")
    ap.add_argument("-l", "--location", type=str, default="San Diego",
                    help="geo location of video feed")
    ap.add_argument("-o", "--output", type=str, default="",
                    help="path to (optional) output video file")
    ap.add_argument("-d", "--display", type=int, default=1,
                    help="whether or not output frame should be displayed")
    ap.add_argument("-w", "--web", type=int, default=1,
                    help="whether to start the program as a flask web app")
    ap.add_argument("-f", "--frame_rate", type=int, default=60,
                    help="the framerate of the video")
    ap.add_argument("-ip", "--ip", type=str, default="0.0.0.0",
                    help="the ip address")
    ap.add_argument("-p", "--port", type=str, default="8000",
                    help="the port number")
    return vars(ap.parse_args())


def main():
    """
    Runs social distancing detector.
    """
    global vs, location

    args = parse_args()
    location = args["location"]
    social_distancing_detector = Detector(args["input"], args["output"], location, args["display"])

    if args["web"] == 1:
        vs = cv2.VideoCapture(args["input"] if args["input"] else 0)
        time.sleep(2.0)

        t = threading.Thread(target=update_video, args=(social_distancing_detector, args["frame_rate"]))
        t.daemon = True
        t.start()
        app.run(host=args["ip"], port=args["port"], debug=True, threaded=True, use_reloader=False)
    else:
        social_distancing_detector.detect_social_distancing()


if __name__ == "__main__":
    main()

vs.stop()
