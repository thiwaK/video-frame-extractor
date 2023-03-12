import sys, argparse

BAR_WIDTH = 60  # ProgressBar Width
FPS_SKIP_RATE = 0.5  # Percentage of frames should skip within a sec. (0.1 = 90%; 0.5 = 50%; 1=0%)
THRESHOLD = 20  # Extract if percentage of difference between two frames greater than THRESHOLD

if __name__ == '__main__':

    parser = argparse.ArgumentParser(
                    prog='Video Frame Extractor',
                    description='This program will extract frames in a video accrding to given conditions',
                    epilog='python vfe.py path/video.mp4')

    parser.add_argument('video_file', help='path to video file')
    parser.add_argument('-s', '--skip-rate', help='Percentage of frames should skip within a sec (0.1=90; 0.5=50; 1=0)')
    parser.add_argument('-t', '--threshold', help='Extract if percentage of difference between two frames greater than THRESHOLD')

    args = parser.parse_args()
    print(args.video_file, args.skip_rate, args.threshold)

    if args.skip_rate:
        FPS_SKIP_RATE = args.skip_rate

    if args.threshold:
        THRESHOLD = args.threshold

    if args.video_file:
        from core import core
        video_file = args.video_file
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
