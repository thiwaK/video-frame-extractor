import cv2, os, sys, time
import numpy as np
import datetime as dt

from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QLabel, QPushButton, QVBoxLayout, \
QHBoxLayout, QWidget, QProgressBar, QLineEdit
from PyQt5.QtGui import QPixmap, QColor, QPainter, QPen, QBrush
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtCore import QObject, QThread, pyqtSignal

from PIL import Image, ImageDraw
from hashlib import sha256


RUN_FLAG = 1            # Flag for run/interupt the process
BAR_WIDTH = 60          # ProgressBar Width
IMAGE_HASH = []         # Uniqe image hash list (use for filtering)
FPS_SKIP_RATE = 0.5     # Amout of frames should skip within a sec
THRESHOLD = 20          # If extract, difference between 2 frames > THRESHOLD

class Worker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)

    def __init__(self, video_file, output_path):
        QThread.__init__(self)
        self.video_file = video_file
        self.output_path = output_path

    def run(self):
        cap = cv2.VideoCapture(self.video_file)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        previous_frame = None
        unique_frame_count = 0
        frame_number = 0

        while RUN_FLAG:
            ret, frame = cap.read()
            if not ret:
                break
            if frame_number % 100 == 0:
                self.progress.emit(int((frame_number/frame_count)*100))
            if previous_frame is None:
                previous_frame = frame
            else:
                mse = np.mean((frame - previous_frame) ** 2)
                if mse > mean_squared_error:
                    out = os.path.join(self.output_path, f"frame_{unique_frame_count}.jpg")
                    cv2.imwrite(out, frame)
                    unique_frame_count += 1
                    previous_frame = frame
            frame_number += 1
        cap.release()
        self.finished.emit()

class ExtractUniqueFrames(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.video_file = None

    def initUI(self):
        self.setWindowTitle("Extract Unique Frames")
        self.setGeometry(100, 100, 500, 150)

        # Create the widgets
        self.select_video_button = QPushButton("Select Video")
        self.select_video_button.setFixedSize(100,40)
        self.select_video_button.clicked.connect(self.select_video)
        self.path_label = QLabel(r"C:\something\something.mp4")

        self.extract_frames_button = QPushButton("Extract Frames")
        self.extract_frames_button.setFixedHeight(50)
        self.extract_frames_button.clicked.connect(self.extract_frames)

        self.painter_label = QLabel()
        self.painter_label.setFixedSize(10,10)
        self.painter_label.setFixedSize(10,10)
    
        self.pbar = QProgressBar(self)
        self.pbar.setAlignment(Qt.AlignLeft)
        self.pixmap_label = QLabel()
        self.pixmap_label.setPixmap(self.get_piximap((50,255,50,255)))
        
        textbox_label = QLabel("Threshold")
        self.textbox = QLineEdit(self)
        self.textbox.setFixedSize(50,25)
        self.textbox.setAlignment(Qt.AlignCenter)
        self.textbox.setText("30")

        # Create the layouts
        brows_layout = QHBoxLayout()
        brows_layout.addWidget(self.select_video_button)
        brows_layout.addWidget(self.path_label)

        buttons_layout = QVBoxLayout()
        buttons_layout.addWidget(self.extract_frames_button)

        pbar_layout = QHBoxLayout()
        pbar_layout.addWidget(self.pbar)
        pbar_layout.addWidget(self.pixmap_label)

        threshold_layout = QHBoxLayout()
        threshold_layout.addStretch()
        threshold_layout.addWidget(QLabel("Threshold"))
        threshold_layout.addWidget(self.textbox)
        threshold_layout.addWidget(QLabel("%"))
        threshold_layout.addStretch()
        
        main_layout = QVBoxLayout()
        main_layout.addLayout(brows_layout)
        main_layout.addLayout(threshold_layout)
        main_layout.addLayout(buttons_layout)
        main_layout.addLayout(pbar_layout)


        # Set the central widget
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        self.thread = QThread()

    def on_stop(self):
        global RUN_FLAG
        self.pixmap_label.setPixmap(self.get_piximap((50,255,50,255)))
        self.pbar.reset()
        self.extract_frames_button.setText("Extract Frames")
        self.thread = QThread()
        RUN_FLAG = 1
        
    def reportProgress(self, n):
        # print(f"Long-Running Step: {n}")
        self.pbar.setValue(n)

    def select_video(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        self.video_file, _ = QFileDialog.getOpenFileName(self, "Select Video", "", "Videos (*.mp4 *.avi *.mkv);;All Files (*)", options=options)
        self.path_label.setText(self.video_file)

    def extract_frames(self):

        if self.thread.isRunning():
            global RUN_FLAG
            RUN_FLAG = 0
            return

        if self.video_file == None:
            self.path_label.setText("ERROR: Invalid_Video_Path")
            return

        try:
            int(str(self.textbox.text()).strip())
        except Exception as e:
            print(e)
            self.path_label.setText("ERROR: Invalid_Threshold_Value")
            self.textbox.setText("30")
            return 

        
        self.pixmap_label.setPixmap(self.get_piximap())
        
        self.worker = Worker(self.video_file, get_output_path(self.video_file))
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.progress.connect(self.reportProgress)

        self.extract_frames_button.setText("STOP")

        if self.video_file:
            self.thread.start()

        self.thread.finished.connect(self.on_stop)
        
    def get_piximap(self, color=(255,50,50,255)):
        img = Image.new("RGBA", (25,25))
        draw = ImageDraw.Draw(img)
        draw.ellipse((0,0,20,20), fill=color, width=0)
        pixmap = QPixmap.fromImage(img.toqimage())
        return pixmap

def end(text_pb, old_time, frame_count, processed_frame_count, items_per_sec):
    print(" "*len(text_pb), end='\r', file=sys.stdout, flush=True)
    time_taked = time.time() - old_time
    H = int(time_taked / (60*60))
    M = int((time_taked % (60*60)) / 60)
    S = int((time_taked % (60*60)) % 60)
    print("{} {}/{} {}/s ET:{}h {}m {}s".format("Completed", processed_frame_count, frame_count, items_per_sec,H,M,S),)

def compare_images(frame, previous_frame, output_path, unique_frame_count):
    mse = np.mean((frame - previous_frame) ** 2)
    if mse > THRESHOLD:
        img_hash = sha256(frame).hexdigest()
        if img_hash in IMAGE_HASH:
            return 0
        IMAGE_HASH.append(img_hash)
        out = os.path.join(output_path, f"frame_{unique_frame_count}.jpg")
        cv2.imwrite(out, frame)
        return 1
    return 0

def get_output_path(video_file):
        fPath, fName = os.path.split(video_file)
        outPath = os.path.join(fPath, fName[:-4])
        if os.path.exists(outPath):
            return outPath
        else:
            os.mkdir(outPath)
            return outPath

def calcProcessTime(starttime, cur_iter, max_iter):

    telapsed = time.time() - starttime
    testimated = (telapsed/cur_iter)*(max_iter)

    finishtime = starttime + testimated
    finishtime = dt.datetime.fromtimestamp(finishtime).strftime("%H:%M:%S")  # in time

    lefttime = testimated-telapsed  # in seconds
    H = int(lefttime//3600)
    M = int((lefttime%3600)/60)
    S = int((lefttime%3600)%60)
    return (int(telapsed), "{}:{}:{}".format(H,M,S), finishtime)

def extract_unique_frames(video_file):
    cap = cv2.VideoCapture(video_file)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    processed_frame_count = 0
    previous_frame = None
    unique_frame_count = 0
    output_path = get_output_path(video_file)
    
    items_per_sec = 0
    old_time = time.time()
    text_pb = ""

    temp_text = "FPS:{} | Total:{} | SkipRate:{} | Valid:{} | Threshold:{}%".format(fps, frame_count, FPS_SKIP_RATE, int(frame_count*FPS_SKIP_RATE), THRESHOLD)
    print("---" + "-"*len(temp_text))
    print(temp_text)
    print("---" + "-"*len(temp_text))
    print()

    while RUN_FLAG:
        ret, frame = cap.read()
        if not ret:
            break
        if processed_frame_count%int((fps*FPS_SKIP_RATE)) != 0:
            processed_frame_count += 1
            continue
        processed_frame_count += 1

        if previous_frame is None:
            previous_frame = np.empty_like(frame)
        else:
            if compare_images(frame, previous_frame, output_path, unique_frame_count):
                unique_frame_count += 1
                previous_frame = frame
        
        x = int(BAR_WIDTH*processed_frame_count/frame_count)
        y = round(processed_frame_count/frame_count*100, 1)
        items_per_sec = int(processed_frame_count/(time.time() - old_time))
        eta = calcProcessTime(old_time, processed_frame_count, frame_count)[1]
        text_pb = "{}[{}{}] {}/{} {}% {}/s ETA:{}".format("Processing", "#"*x, "."*(BAR_WIDTH-x), processed_frame_count, frame_count, y, items_per_sec, eta)
        
        print(text_pb, end='\r', file=sys.stdout, flush=True)

        
    cap.release()
    
    end(text_pb, old_time, frame_count, processed_frame_count, items_per_sec)



if __name__ == '__main__':
    if len(sys.argv) >= 1:
        video_file = sys.argv[1]
        try:
            extract_unique_frames(video_file)
        except KeyboardInterrupt as e:
            RUN_FLAG = 0
        

    else:
        app = QApplication(sys.argv)
        window = ExtractUniqueFrames()
        window.show()
        sys.exit(app.exec_())