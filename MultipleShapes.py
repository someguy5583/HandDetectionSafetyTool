from PIL import Image
from .transforms import RGBTransform
import random

import cv2
import mediapipe as mp
import time
import colorsys

from .Rectangle import Rectangle
from .Circle import Circle
from .Polygon import Polygon

cap = cv2.VideoCapture(0)
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
mp_draw = mp.solutions.drawing_utils
prev_t = 0
curr_t = 0

shapes = []

try:
    with open("output.txt", "r") as text_file:
        for line in text_file:
            color = colorsys.hsv_to_rgb(random.random(), random.random() * .5 + .5, 1)
            color = (color[0] * 255, color[1] * 255, color[2] * 255)

            sus = line.split('|')
            print(sus)
            if sus[0] == "Rect":
                shapes.append(Rectangle(Rectangle.read(sus[1]), color, cv2.imread(f'shape{len(shapes)}.jpeg')))
            elif sus[0] == "Circle":
                shapes.append(Circle(Circle.read(sus[1]), color, cv2.imread(f'shape{len(shapes)}.jpeg')))
            else:
                shapes.append(Polygon(Polygon.read(sus[1]), color, cv2.imread(f'shape{len(shapes)}.jpeg')))

except:
    print("sussy")
    pass

save_button = [(512, 7), (635, 60)]
update_button = [(712, 7), (935, 60)]
new_button = [(1012, 7), (1135, 60)]

is_updating = False
creating_new_shape = False
creating_poly = False
was_down = False
shape_index = 0
shape_type = 0


def on_mouse_event(event, x, y, flags, param):
    global shapes, was_down, shape_index, shape_type

    # check buttons
    if event == cv2.EVENT_LBUTTONDOWN or event == cv2.EVENT_LBUTTONUP:
        if on_button_click(x, y):
            return

    # create new shape
    if event == cv2.EVENT_LBUTTONDOWN and creating_new_shape:
        positions = [[x, y], [x, y]]
        color = colorsys.hsv_to_rgb(random.random(), random.random() * .5 + .5, 1)
        color = (color[0] * 255, color[1] * 255, color[2] * 255)
        if shape_type == 0:
            shapes.append(Rectangle(positions, color))
        elif shape_type == 1:
            shapes.append(Circle(positions, color))

        if creating_poly:
            shapes[shape_index].add_position([x, y])
        else:
            shape_index = len(shapes) - 1

    # update shape
    if is_updating:
        if event == cv2.EVENT_LBUTTONDOWN and not creating_poly:
            was_down = True
            positions = [[x, y], [x, y]]
            shapes[shape_index].set_positions(positions)
        elif was_down and event == cv2.EVENT_MOUSEMOVE:
            print(shape_index)
            pos1 = shapes[shape_index].get_positions()[0]
            positions = [pos1, [x, y]]
            shapes[shape_index].set_positions(positions)
        if event == cv2.EVENT_LBUTTONUP:
            was_down = False


def on_button_click(x, y):
    global is_updating, creating_new_shape, shape_index

    # save
    if min(save_button[0][0], save_button[1][0]) <= x <= max(save_button[0][0], save_button[1][0]):
        if min(save_button[0][1], save_button[1][1]) <= y <= max(save_button[0][1], save_button[1][1]):
            with open("output.txt", "w") as text_file:
                for shape in shapes:
                    text_file.write(str(shape) + "\n")

            for i in range(len(shapes)):
                shapes[i].save(f"shape{i}.jpeg", img)

            is_updating = False
            creating_new_shape = False

            return True
    # update
    elif min(update_button[0][0], update_button[1][0]) <= x <= max(update_button[0][0], update_button[1][0]):
        if min(update_button[0][1], update_button[1][1]) <= y <= max(update_button[0][1], update_button[1][1]):
            print("update")
            is_updating = True
            return True
    # new
    elif min(new_button[0][0], new_button[1][0]) <= x <= max(new_button[0][0], new_button[1][0]):
        if min(new_button[0][1], new_button[1][1]) <= y <= max(new_button[0][1], new_button[1][1]):
            creating_new_shape = True
            is_updating = True
            return True

    return False


cv2.namedWindow("Image")
cv2.setMouseCallback('Image', on_mouse_event)

while True:
    global img, success
    success, img = cap.read()
    img = cv2.flip(img, 1)
    img = cv2.resize(img, (1280, 720))
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    pil_image = Image.fromarray(imgRGB)
    white = RGBTransform().mix_with((224, 172, 105), factor=.30).applied_to(pil_image)
    results = hands.process(imgRGB)

    if not is_updating:
        for shape in shapes:
            shape.track(img)

    for i in range(len(shapes)):
        shapes[i].render(img, 6, i, is_updating)

    # render hand
    if results.multi_hand_landmarks and not is_updating:
        for handLms in results.multi_hand_landmarks:
            for id, lm in enumerate(handLms.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)

                # check if any landmarks are in the alert rect
                for shape in shapes:
                    if shape.check_point(cx, cy):
                        cv2.rectangle(img, (0, 0), (100, 100), (0, 0, 255), -1)

            mp_draw.draw_landmarks(img, handLms, mp_hands.HAND_CONNECTIONS)

    # render buttons
    cv2.rectangle(img, save_button[0], save_button[1], (0, 0, 255), -1)
    cv2.rectangle(img, update_button[0], update_button[1],
                  (0, 0, 255) if not is_updating else (0, 255, 255), -1)
    cv2.rectangle(img, new_button[0], new_button[1],
                  (0, 0, 255) if not creating_new_shape else (0, 255, 255), -1)
    cv2.putText(img, "Update", (update_button[0][0], update_button[1][1]), cv2.FONT_HERSHEY_PLAIN, 3, (255, 255, 255),
                3)
    cv2.putText(img, "Save",
                (save_button[0][0], save_button[1][1]),
                cv2.FONT_HERSHEY_PLAIN, 3, (255, 255, 255), 3)
    cv2.putText(img, "New",
                (new_button[0][0], new_button[1][1]),
                cv2.FONT_HERSHEY_PLAIN, 3, (255, 255, 255), 3)
    # cv2.putText(img, f"Camera Position > {str(delta)}", (0, 710), cv2.FONT_HERSHEY_PLAIN, 3, (0, 0, 255), 2)

    curr_t = time.time()
    fps = 1 / (curr_t - prev_t)
    prev_t = curr_t
    cv2.imshow("Image", img)

    key = cv2.waitKey(1)
    if key == 27:
        break
    elif key == ord('r'):
        shape_type = 0
    elif key == ord('c'):
        shape_type = 1
    elif key == ord('p'):
        shape_type = 2
        if creating_new_shape:
            creating_poly = True
            if len(shapes) != 0 and len(shapes[shape_index].positions) == 0:
                shapes.pop(shape_index)
            color = colorsys.hsv_to_rgb(random.random(), random.random() * .5 + .5, 1)
            color = (color[0] * 255, color[1] * 255, color[2] * 255)
            shapes.append(Polygon([], color))
            shape_index = len(shapes)-1
    elif ord('0') <= key <= ord('9'):
        print(key - ord('0'))
        shape_index = key - ord('0')
    elif key == 127 and is_updating and len(shapes) > 0:
        shapes.pop(shape_index)
        shape_index -= 1
    elif key != -1:
        print(key)

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
