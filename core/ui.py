from PIL import Image, ImageDraw
from PyQt5.QtCore import Qt, QObject, QThread, pyqtSignal
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QHBoxLayout, QWidget, QProgressBar, QLineEdit
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QLabel, QPushButton, QVBoxLayout
import core as core_module


def get_pixmap(color=(255, 50, 50, 255)):
    img = Image.new("RGBA", (25, 25))
    draw = ImageDraw.Draw(img)
    draw.ellipse((0, 0, 20, 20), fill=color, width=0)
    pixmap = QPixmap.fromImage(img.toqimage())
    return pixmap


class Worker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)
    core = None

    def __init__(self, video_file):
        print(video_file)
        QThread.__init__(self)
        self.video_file = video_file
        self.core = core_module.Core(video_file)
        self.output_path = self.core.get_output_path()

    def run(self):
        self.core.extract_unique_frames()
        self.finished.emit()


class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.thread = None
        self.video_file = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Extract Unique Frames")
        self.setGeometry(100, 100, 500, 150)

        # Create the widgets
        self.select_video_button = QPushButton("Select Video")
        self.select_video_button.setFixedSize(100, 40)
        self.select_video_button.clicked.connect(self.select_video)
        self.path_label = QLabel(r"C:\something\something.mp4")

        self.extract_frames_button = QPushButton("Extract Frames")
        self.extract_frames_button.setFixedHeight(50)
        self.extract_frames_button.clicked.connect(self.extract_frames)

        self.painter_label = QLabel()
        self.painter_label.setFixedSize(10, 10)
        self.painter_label.setFixedSize(10, 10)

        self.pbar = QProgressBar(self)
        self.pbar.setAlignment(Qt.AlignLeft)
        self.pixmap_label = QLabel()
        self.pixmap_label.setPixmap(get_pixmap((50, 255, 50, 255)))

        textbox_label = QLabel("Threshold")
        self.textbox = QLineEdit(self)
        self.textbox.setFixedSize(50, 25)
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
        self.pixmap_label.setPixmap(get_pixmap((50, 255, 50, 255)))
        self.pbar.reset()
        self.extract_frames_button.setText("Extract Frames")
        self.thread = QThread()
        self.core.RUN_FLAG = 1

    def report_progress(self, n):
        # print(f"Long-Running Step: {n}")
        self.pbar.setValue(n)

    def select_video(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        self.video_file, _ = QFileDialog.getOpenFileName(self, "Select Video", "",
                                                         "Videos (*.mp4 *.avi *.mkv);;All Files (*)", options=options)
        self.path_label.setText(self.video_file)

    def extract_frames(self):

        if self.thread.isRunning():
            self.core.RUN_FLAG = 0
            return

        if self.video_file is None:
            self.path_label.setText("ERROR: Invalid_Video_Path")
            return

        try:
            int(str(self.textbox.text()).strip())
        except Exception as e:
            print(e)
            self.path_label.setText("ERROR: Invalid_Threshold_Value")
            self.textbox.setText("30")
            return

        self.pixmap_label.setPixmap(get_pixmap())

        self.worker = Worker(self.video_file)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.progress.connect(self.report_progress)

        self.extract_frames_button.setText("STOP")

        if self.video_file:
            self.core = core_module.Core(self.video_file)
            self.worker.core = self.core
            self.thread.start()

        self.thread.finished.connect(self.on_stop)
