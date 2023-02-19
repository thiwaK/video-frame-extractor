import cv2, os, sys, time
import numpy as np
import datetime as dt
from hashlib import sha256

unique_frame_count = 0  # Number of unique frames extracted
RUN_FLAG = 1  # Flag for run/interrupt the process
IMAGE_HASH = []  # Unique image hash list (use for filtering)
FPS_SKIP_RATE = 0.5
THRESHOLD = 20
BAR_WIDTH = 60


def seconds_to_hms(time_in_sec):
    h = int(time_in_sec // 3600)
    m = int((time_in_sec % 3600) / 60)
    s = int((time_in_sec % 3600) % 60)

    return h, m, s


def get_eta(start_time, cur_iter, max_iter):
    elapsed = time.time() - start_time
    estimated = (elapsed / cur_iter) * max_iter

    finished = start_time + estimated
    finished = dt.datetime.fromtimestamp(finished).strftime("%H:%M:%S")  # in time

    left = estimated - elapsed  # in seconds
    h, m, s = seconds_to_hms(left)
    return int(elapsed), "{}:{}:{}".format(h, m, s), finished


class Core:

    def __init__(self, video_file):
        self.video_file = video_file
        self.output_path = self.get_output_path()
        self.unique_frame_count = 0
        self.RUN_FLAG = RUN_FLAG
        self.IMAGE_HASH = IMAGE_HASH
        self.FPS_SKIP_RATE = FPS_SKIP_RATE
        self.THRESHOLD = THRESHOLD
        self.BAR_WIDTH = BAR_WIDTH

    def compare_frames(self, current_frame, previous_frame):
        mse = np.mean((current_frame - previous_frame) ** 2)
        if mse > self.THRESHOLD:
            img_hash = sha256(current_frame).hexdigest()
            if img_hash in self.IMAGE_HASH:
                return 0
            self.IMAGE_HASH.append(img_hash)
            out = os.path.join(self.output_path, f"frame_{self.unique_frame_count}.jpg")
            cv2.imwrite(out, current_frame)
            self.unique_frame_count += 1
            return 1
        return 0

    def get_output_path(self):

        f_path, f_name = os.path.split(self.video_file)
        out_path = os.path.join(f_path, os.path.splitext(f_name)[0])

        if os.path.exists(out_path):
            return out_path
        else:
            os.mkdir(out_path)
            return out_path

    def extract_unique_frames(self):

        cap = cv2.VideoCapture(self.video_file)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)

        processed_frame_count = 0
        previous_frame = None

        items_per_sec = 0
        old_time = time.time()

        text_pb = ""
        temp_text = "FPS:{} | Total:{} | SkipRate:{} | Valid:{} | Threshold:{}%"
        temp_text.format(fps, frame_count, self.FPS_SKIP_RATE, int(frame_count * self.FPS_SKIP_RATE), self.THRESHOLD)
        print("---" + "-" * len(temp_text))
        print(temp_text)
        print("---" + "-" * len(temp_text))
        print()

        while self.RUN_FLAG:
            ret, frame = cap.read()
            if not ret:
                break
            if processed_frame_count % int((fps * self.FPS_SKIP_RATE)) != 0:
                processed_frame_count += 1
                continue
            processed_frame_count += 1

            if previous_frame is None:
                previous_frame = np.empty_like(frame)
            else:
                if self.compare_frames(frame, previous_frame):
                    self.unique_frame_count += 1
                    previous_frame = frame

            x = int(self.BAR_WIDTH * processed_frame_count / frame_count)
            y = round(processed_frame_count / frame_count * 100, 1)
            items_per_sec = int(processed_frame_count / (time.time() - old_time))
            eta = get_eta(old_time, processed_frame_count, frame_count)[1]
            text_pb = "{}[{}{}] {}/{} {}% {}/s ETA:{}".format("Processing", "#" * x, "." * (self.BAR_WIDTH - x),
                                                              processed_frame_count, frame_count, y, items_per_sec, eta)

            print(text_pb, end='\r', file=sys.stdout, flush=True)

        cap.release()
        print(" " * len(text_pb), end='\r', file=sys.stdout, flush=True)
        h, m, s = seconds_to_hms(time.time() - old_time)
        print("{} {}/{} {}/s ElapsedTime:{}h {}m {}s".format("Completed", processed_frame_count,
                                                             frame_count, items_per_sec, h, m, s), )
