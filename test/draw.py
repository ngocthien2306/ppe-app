import cv2

# Tạo một biến toàn cục để lưu trữ tọa độ của điểm bắt đầu và điểm kết thúc khi vẽ rectangle
start_point = (-1, -1)
end_point = (-1, -1)
drawing = False

def draw_rectangle(event, x, y, flags, param):
    global start_point, end_point, drawing

    if event == cv2.EVENT_LBUTTONDOWN:
        start_point = (x, y)
        end_point = (x, y)
        drawing = True
    elif event == cv2.EVENT_LBUTTONUP:
        end_point = (x, y)
        drawing = False
        cv2.rectangle(img, start_point, end_point, (0, 255, 0), 2)
        cv2.imshow('image', img)
    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing:
            end_point = (x, y)
            temp_img = img.copy()
            cv2.rectangle(temp_img, start_point, end_point, (0, 255, 0), 2)
            cv2.imshow('image', temp_img)


# Tạo cửa sổ và liên kết sự kiện chuột với hàm vẽ rectangle
cv2.namedWindow('image')
cv2.setMouseCallback('image', draw_rectangle)
img = cv2.imread('test/test.png')
while True:
    cv2.imshow('image', img)
    key = cv2.waitKey(1) & 0xFF
    print(start_point, end_point)
    if key == 27:  # Nhấn ESC để thoát
        break

cv2.destroyAllWindows()
