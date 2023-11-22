import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import cv2
import os
from utils.image_utils import center_crop

class HomeWindow(tk.Tk):
    def __init__(self):
        super().__init__()

        # Set up the main window with a 9:16 aspect ratio
        width = 600
        aspect_ratio = 9 / 16  # 9:16
        height = int(width / aspect_ratio)
        self.geometry(f"{width}x{height}")
        self.title("Your Title Here")

        # Create a container frame to hold camera and button
        container_frame = ttk.Frame(self)
        container_frame.pack(fill=tk.BOTH, expand=True)

        # Set background image
        background_image = ImageTk.PhotoImage(file="ui/assets/images/background.png")
        background_label = tk.Label(container_frame, image=background_image)
        background_label.place(x=0, y=0, relwidth=1, relheight=1)

        # Create a Label to display the camera feed
        self.camera_label = tk.Label(container_frame)
        self.camera_label.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Create a Button
        button_image_path = os.path.join("ui/assets/icon", "icons8-checkmark-64.svg")  # Replace with your icon path
        button_image = ImageTk.PhotoImage(file=button_image_path)

        button = ttk.Button(
            container_frame,
            text="KIỂM TRA PPE",
            command=self.start_camera,
            image=button_image,
            compound=tk.LEFT,
            style="Custom.TButton"
        )
        button.pack(side=tk.BOTTOM, fill=tk.X)

        # Define custom style for the button
        self.style = ttk.Style()
        self.style.configure("Custom.TButton",
                             font=("Roboto", 32, "bold"),
                             background="#21618C",
                             foreground="white",
                             borderwidth=0)

        # OpenCV variables
        self.camera = cv2.VideoCapture(0)
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

        self.start_camera()  # Update the camera display initially

    def start_camera(self):
        # Start the camera
        self.after(33, self.update_camera)  # Update every 33 milliseconds (approximately 30 fps)

    def update_camera(self):
        ret, frame = self.camera.read()
        if ret:
            frame_copy = frame.copy()
            size = (self.winfo_width(), self.winfo_height())
            frame_crop = center_crop(frame_copy, size)  # Crop width, keeping height constant
            resized_image = cv2.resize(frame_crop, size[::-1])

            # Convert OpenCV image to PIL format
            image = Image.fromarray(cv2.cvtColor(resized_image, cv2.COLOR_BGR2RGB))
            imgtk = ImageTk.PhotoImage(image=image)

            # Set the Image as the image for the Label
            self.camera_label.imgtk = imgtk
            self.camera_label.config(image=imgtk)

            # Schedule the next update
            self.after(33, self.update_camera)

    def on_close(self):
        # Stop the camera when the application is closed
        self.camera.release()
        self.destroy()

# Create an instance of the HomeWindow class
app = HomeWindow()

# Configure the close event
app.protocol("WM_DELETE_WINDOW", app.on_close)

# Start the Tkinter main loop
app.mainloop()
