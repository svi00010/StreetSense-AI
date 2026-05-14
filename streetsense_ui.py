import customtkinter as ctk
import cv2
import threading
import time
from ultralytics import YOLO
from PIL import Image
import numpy as np

# ==========================================
# APPEARANCE
# ==========================================

ctk.set_appearance_mode("dark")

# ==========================================
# MODEL + VIDEO
# ==========================================

model = YOLO("yolo11s-seg.pt")
video_path = "dashcam.mp4"

# ==========================================
# COLORS
# ==========================================

BG = "#121212"
CARD = "#1C1C1E"
CARD_2 = "#2C2C2E"

TEXT = "#F5F5F7"
SUBTEXT = "#8E8E93"

ACCENT = "#FF7A45"
ACCENT_HOVER = "#ff946b"

GREEN = "#32D74B"

# ==========================================
# WINDOW
# ==========================================

app = ctk.CTk()

app.title("StreetSense AI")
app.geometry("1600x900")
app.configure(fg_color=BG)

running = False

# ==========================================
# TOP BAR
# ==========================================

topbar = ctk.CTkFrame(
    app,
    fg_color=BG,
    height=70
)

topbar.pack(fill="x", padx=24, pady=(14, 0))

# ==========================================
# TITLE
# ==========================================

title_frame = ctk.CTkFrame(
    topbar,
    fg_color="transparent"
)

title_frame.pack(side="left", pady=10)

ctk.CTkLabel(
    title_frame,
    text="StreetSense AI",
    font=ctk.CTkFont(
        family="Helvetica",
        size=28,
        weight="bold"
    ),
    text_color=TEXT
).pack(anchor="w")

ctk.CTkLabel(
    title_frame,
    text="Advanced ADAS Perception Dashboard",
    font=ctk.CTkFont(size=12),
    text_color=SUBTEXT
).pack(anchor="w", pady=(2, 0))

# ==========================================
# STATUS
# ==========================================

status_frame = ctk.CTkFrame(
    topbar,
    fg_color=CARD,
    corner_radius=20
)

status_frame.pack(side="right", pady=10)

status_dot = ctk.CTkLabel(
    status_frame,
    text="●",
    font=ctk.CTkFont(size=18),
    text_color="#777777"
)

status_dot.pack(side="left", padx=(14, 6))

status_label = ctk.CTkLabel(
    status_frame,
    text="System Idle",
    font=ctk.CTkFont(size=13),
    text_color=TEXT
)

status_label.pack(side="left", padx=(0, 14))

# ==========================================
# MAIN LAYOUT
# ==========================================

main = ctk.CTkFrame(
    app,
    fg_color="transparent"
)

main.pack(
    fill="both",
    expand=True,
    padx=24,
    pady=20
)

main.grid_columnconfigure(0, weight=4)
main.grid_columnconfigure(1, weight=1)

# ==========================================
# VIDEO CONTAINER
# ==========================================

video_container = ctk.CTkFrame(
    main,
    fg_color=CARD,
    corner_radius=28
)

video_container.grid(
    row=0,
    column=0,
    sticky="nsew",
    padx=(0, 14)
)

video_container.grid_propagate(False)

# ==========================================
# VIDEO HEADER
# ==========================================

video_header = ctk.CTkFrame(
    video_container,
    fg_color="transparent"
)

video_header.pack(fill="x", padx=18, pady=(16, 0))

ctk.CTkLabel(
    video_header,
    text="Live Dashcam Feed",
    font=ctk.CTkFont(size=18, weight="bold"),
    text_color=TEXT
).pack(side="left")

# ==========================================
# VIDEO LABEL
# ==========================================

DISPLAY_WIDTH = 1100
DISPLAY_HEIGHT = 700

video_label = ctk.CTkLabel(
    video_container,
    text="Press Run Detection to start",
    text_color="#666",
    fg_color="#101010",
    corner_radius=22,
    font=ctk.CTkFont(size=14),
    width=DISPLAY_WIDTH,
    height=DISPLAY_HEIGHT
)

video_label.pack(
    padx=18,
    pady=(10, 18)
)

video_label.pack_propagate(False)

# ==========================================
# SIDEBAR
# ==========================================

sidebar = ctk.CTkScrollableFrame(
    main,
    width=300,
    fg_color=CARD,
    corner_radius=28
)

sidebar.grid(
    row=0,
    column=1,
    sticky="ns"
)

sidebar._scrollbar.configure(width=6)

# ==========================================
# BUTTONS
# ==========================================

button_frame = ctk.CTkFrame(
    sidebar,
    fg_color="transparent"
)

button_frame.pack(
    fill="x",
    padx=18,
    pady=(18, 10)
)

ctk.CTkButton(
    button_frame,
    text="Run Detection",
    command=lambda: start(),
    fg_color=ACCENT,
    hover_color=ACCENT_HOVER,
    text_color="white",
    font=ctk.CTkFont(size=14, weight="bold"),
    corner_radius=14,
    height=48
).pack(fill="x")

ctk.CTkButton(
    button_frame,
    text="Stop",
    command=lambda: stop(),
    fg_color=CARD_2,
    hover_color="#3A3A3C",
    text_color=TEXT,
    font=ctk.CTkFont(size=14),
    corner_radius=14,
    height=44
).pack(fill="x", pady=(10, 0))

# ==========================================
# STATS
# ==========================================

ctk.CTkLabel(
    sidebar,
    text="SYSTEM METRICS",
    font=ctk.CTkFont(size=11),
    text_color=SUBTEXT
).pack(anchor="w", padx=22, pady=(14, 8))


def make_stat(title, value):

    card = ctk.CTkFrame(
        sidebar,
        fg_color=CARD_2,
        corner_radius=20,
        height=90
    )

    card.pack(fill="x", padx=18, pady=6)

    inner = ctk.CTkFrame(
        card,
        fg_color="transparent"
    )

    inner.pack(anchor="w", padx=18, pady=14)

    ctk.CTkLabel(
        inner,
        text=title,
        font=ctk.CTkFont(size=11),
        text_color=SUBTEXT
    ).pack(anchor="w")

    value_label = ctk.CTkLabel(
        inner,
        text=value,
        font=ctk.CTkFont(size=30, weight="bold"),
        text_color=TEXT
    )

    value_label.pack(anchor="w")

    return value_label


stat_v = make_stat("Vehicles", "0")
stat_p = make_stat("Pedestrians", "0")
stat_s = make_stat("Signs", "0")
stat_f = make_stat("FPS", "0")
stat_t = make_stat("Traffic Light", "None")

# ==========================================
# ALERTS
# ==========================================

ctk.CTkLabel(
    sidebar,
    text="LIVE ALERTS",
    font=ctk.CTkFont(size=11),
    text_color=SUBTEXT
).pack(anchor="w", padx=22, pady=(18, 8))

danger_frame = ctk.CTkFrame(
    sidebar,
    fg_color="#2A1515",
    corner_radius=18,
    height=70
)

danger_frame.pack(fill="x", padx=18)

danger_label = ctk.CTkLabel(
    danger_frame,
    text="No active alerts",
    font=ctk.CTkFont(size=13, weight="bold"),
    text_color="#ff9999"
)

danger_label.pack(padx=14, pady=20)

# ==========================================
# ALERT LOG
# ==========================================

ctk.CTkLabel(
    sidebar,
    text="ALERT LOG",
    font=ctk.CTkFont(size=11),
    text_color=SUBTEXT
).pack(anchor="w", padx=22, pady=(18, 8))

alert_box = ctk.CTkTextbox(
    sidebar,
    fg_color=CARD_2,
    corner_radius=20,
    border_width=0,
    text_color="#b5b5b5",
    font=ctk.CTkFont(size=11),
    height=220
)

alert_box.pack(
    fill="both",
    expand=True,
    padx=18,
    pady=(0, 18)
)

alert_box.configure(state="disabled")

# ==========================================
# ALERT LOGGER
# ==========================================

def log_alert(msg):

    alert_box.configure(state="normal")

    alert_box.insert(
        "end",
        f"[{time.strftime('%H:%M:%S')}] {msg}\n"
    )

    alert_box.see("end")

    alert_box.configure(state="disabled")

# ==========================================
# DETECTION LOOP
# ==========================================

def run_detection():

    global running

    cap = cv2.VideoCapture(video_path)

    frame_count = 0
    prev_time = time.time()

    while cap.isOpened() and running:

        ret, frame = cap.read()

        if not ret:
            break

        frame_count += 1

        if frame_count % 3 != 0:
            continue

        results = model(
            frame,
            conf=0.20,
            verbose=False
        )

        annotated = frame.copy()

        vehicle_count = 0
        person_count = 0
        sign_count = 0

        pedestrian_danger = False
        vehicle_danger = False

        traffic_light_state = "None"

        # ==========================================
        # ROAD HIGHLIGHTING
        # ==========================================

        overlay = annotated.copy()

        polygon = np.array([
            [
                (0, frame.shape[0]),
                (frame.shape[1] * 0.4, frame.shape[0] * 0.6),
                (frame.shape[1] * 0.6, frame.shape[0] * 0.6),
                (frame.shape[1], frame.shape[0])
            ]
        ], dtype=np.int32)

        cv2.fillPoly(
            overlay,
            polygon,
            (50, 180, 80)
        )

        annotated = cv2.addWeighted(
            overlay,
            0.25,
            annotated,
            0.75,
            0
        )

        # ==========================================
        # DETECTIONS
        # ==========================================

        for box in results[0].boxes:

            cls = int(box.cls[0])
            label = model.names[cls]

            x1, y1, x2, y2 = map(
                int,
                box.xyxy[0]
            )

            box_height = y2 - y1

            # ==========================================
            # VEHICLES
            # ==========================================

            if label in [
                "car",
                "truck",
                "bus",
                "motorcycle"
            ]:

                vehicle_count += 1

                cv2.rectangle(
                    annotated,
                    (x1, y1),
                    (x2, y2),
                    (255, 180, 0),
                    2
                )

                if (
                    box_height > frame.shape[0] * 0.35
                    and
                    y2 > frame.shape[0] * 0.7
                ):

                    vehicle_danger = True

            # ==========================================
            # PEDESTRIANS
            # ==========================================

            if label == "person":

                person_count += 1

                cv2.rectangle(
                    annotated,
                    (x1, y1),
                    (x2, y2),
                    (0, 255, 255),
                    2
                )

                if box_height > frame.shape[0] * 0.3:
                    pedestrian_danger = True

            # ==========================================
            # STOP SIGN
            # ==========================================

            if label == "stop sign":
                sign_count += 1

            # ==========================================
            # TRAFFIC LIGHT
            # ==========================================

            if label == "traffic light":

                roi = frame[y1:y2, x1:x2]

                if roi.size > 0:

                    hsv = cv2.cvtColor(
                        roi,
                        cv2.COLOR_BGR2HSV
                    )

                    red_mask = cv2.inRange(
                        hsv,
                        (0, 120, 120),
                        (10, 255, 255)
                    )

                    green_mask = cv2.inRange(
                        hsv,
                        (40, 50, 50),
                        (90, 255, 255)
                    )

                    red_pixels = cv2.countNonZero(red_mask)
                    green_pixels = cv2.countNonZero(green_mask)

                    if red_pixels > green_pixels:
                        traffic_light_state = "RED"
                    else:
                        traffic_light_state = "GREEN"

                cv2.rectangle(
                    annotated,
                    (x1, y1),
                    (x2, y2),
                    (0, 0, 255),
                    2
                )

                cv2.putText(
                    annotated,
                    traffic_light_state,
                    (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 0, 255),
                    2
                )

        # ==========================================
        # FPS
        # ==========================================

        curr_time = time.time()
        fps = 1 / (curr_time - prev_time)
        prev_time = curr_time

        # ==========================================
        # UPDATE UI
        # ==========================================

        stat_v.configure(text=str(vehicle_count))
        stat_p.configure(text=str(person_count))
        stat_s.configure(text=str(sign_count))
        stat_f.configure(text=f"{fps:.1f}")
        stat_t.configure(text=traffic_light_state)

        # ==========================================
        # WARNINGS
        # ==========================================

        if pedestrian_danger:

            danger_label.configure(
                text="⚠ Pedestrian Too Close"
            )

            log_alert(
                "Pedestrian proximity warning"
            )

        elif vehicle_danger:

            danger_label.configure(
                text="⚠ Vehicle Too Close"
            )

            log_alert(
                "Forward collision warning"
            )

        else:

            danger_label.configure(
                text="No active alerts"
            )

        if traffic_light_state == "RED":

            log_alert(
                "Red traffic light detected"
            )

        # ==========================================
        # VIDEO RENDER
        # ==========================================

        annotated = cv2.resize(
            annotated,
            (DISPLAY_WIDTH, DISPLAY_HEIGHT)
        )

        annotated_rgb = cv2.cvtColor(
            annotated,
            cv2.COLOR_BGR2RGB
        )

        img = Image.fromarray(
            annotated_rgb
        )

        ctk_img = ctk.CTkImage(
            light_image=img,
            dark_image=img,
            size=(DISPLAY_WIDTH, DISPLAY_HEIGHT)
        )

        video_label.configure(
            image=ctk_img,
            text=""
        )

        video_label.image = ctk_img

    cap.release()

    running = False

    status_label.configure(
        text="System Idle"
    )

    status_dot.configure(
        text_color="#777777"
    )

# ==========================================
# START
# ==========================================

def start():

    global running

    if running:
        return

    running = True

    status_label.configure(
        text="System Active"
    )

    status_dot.configure(
        text_color=GREEN
    )

    threading.Thread(
        target=run_detection,
        daemon=True
    ).start()

# ==========================================
# STOP
# ==========================================

def stop():

    global running

    running = False

    status_label.configure(
        text="System Idle"
    )

    status_dot.configure(
        text_color="#777777"
    )

    danger_label.configure(
        text="No active alerts"
    )

# ==========================================
# MAIN LOOP
# ==========================================

app.mainloop()