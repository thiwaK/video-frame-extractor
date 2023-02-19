import sys

BAR_WIDTH = 60  # ProgressBar Width
FPS_SKIP_RATE = 0.5  # Percentage of frames should skip within a sec. (0.1 = 90%; 0.5 = 50%; 1=0%)
THRESHOLD = 20  # Extract if percentage of difference between two frames greater than THRESHOLD

if __name__ == '__main__':

    if len(sys.argv) > 1:
        from core import core
        video_file = sys.argv[1]
        try:
            c = core.Core(video_file)
            c.BAR_WIDTH = BAR_WIDTH
            c.FPS_SKIP_RATE = FPS_SKIP_RATE
            c.THRESHOLD = THRESHOLD
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
