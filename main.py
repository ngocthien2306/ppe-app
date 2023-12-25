import argparse
from PyQt5.QtWidgets import QApplication
import sys
import subprocess
from ui.flash import FlashWindow
from PyQt5.QtCore import Qt, QCoreApplication

def on_application_exit():
    # This function will be called when the application is about to exit
    print("Application is about to exit.")


def main(mode):
    if mode == 'deploy':
        from ui.home import HomeWindow as MainWindow
    elif mode == 'collect':
        from ui.collect_data import CollectWindow as MainWindow

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
