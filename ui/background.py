import tkinter as tk
import cv2

def get_screen_resolution():
    root = tk.Tk()
    root.attributes("-fullscreen", True)
    root.update_idletasks()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    root.destroy()
    return screen_width, screen_height


def show_background(time_ms=3000):
    screen_width, screen_height = get_screen_resolution()
    background_image = cv2.imread('public/assets/images/background.png')
    print(background_image.shape)
    resized_background = cv2.resize(background_image, (1080, 1920))
    
    x = (screen_width - resized_background.shape[1]) // 2
    y = (screen_height - resized_background.shape[0]) // 2

    # Create a window for the background image with the toolbar
    cv2.namedWindow('PPE Background', cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty('PPE Background',cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)
    cv2.moveWindow('PPE Background', x, y)
    cv2.imshow('PPE Background', resized_background)
    cv2.waitKey(time_ms) 
    cv2.destroyAllWindows()
    
    