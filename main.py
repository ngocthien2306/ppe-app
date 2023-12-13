import argparse
from PyQt5.QtWidgets import QApplication
import sys
from ui.background import show_background
import subprocess
from ui.flash import FlashWindow
def main(mode):
    if mode == 'deploy':
        from ui.home import HomeWindow as MainWindow
    elif mode == 'collect':
        from ui.collect_data import CollectWindow as MainWindow

    # show_background()
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Script description.')

    parser.add_argument('--mode', choices=['deploy', 'collect'], default='deploy', help='Select the mode')

    args = parser.parse_args()

    main(args.mode)

    command = "sh ~/.xprofile"
    subprocess.run(command, shell=True)
