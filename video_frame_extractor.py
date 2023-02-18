import sys
from core import core

BAR_WIDTH = 60  # ProgressBar Width
IMAGE_HASH = []  # Unique image hash list (use for filtering)
FPS_SKIP_RATE = 0.5  # Amount of frames should skip within a sec
THRESHOLD = 20  # Extract if difference between 2 frames > THRESHOLD

if __name__ == '__main__':

    if len(sys.argv) > 1:
        video_file = sys.argv[1]
        try:
            c = core.Core(video_file)
            c.extract_unique_frames()
        except KeyboardInterrupt as e:
            RUN_FLAG = 0

    else:
        from core.ui import App
        from PyQt5.QtWidgets import QApplication

        app = QApplication(sys.argv)
        window = App()
        window.show()
        sys.exit(app.exec_())
