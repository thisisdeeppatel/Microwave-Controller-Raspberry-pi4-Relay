import tkinter as tk
import RPi.GPIO as GPIO

root = tk.Tk()
root.title("MACHINE SCREEN")
root.attributes("-fullscreen", True)

FONT = ("Arial", 30)
delay_time = 1000

# exit full screen on esc
def exit_full_screen(event):
    window_width = 1080
    window_height = 800
    root.geometry(f"{window_width}x{window_height}+0+0")
    root.attributes("-fullscreen", False)
    GPIO.cleanup() # releases controls of gpio on exit


root.bind("<Escape>", exit_full_screen)  # bind esc button to trigger function

# define gpio pins of raspberry pi 4
PREHEAT_PIN = 17
MICROWAVE_PIN = 27
GRILL_PIN = 22
CONVECTION_PIN = 5

GPIO.setmode(GPIO.BCM) # set mode
GPIO.setup(PREHEAT_PIN, GPIO.OUT)
GPIO.setup(MICROWAVE_PIN, GPIO.OUT)
GPIO.setup(GRILL_PIN, GPIO.OUT)
GPIO.setup(CONVECTION_PIN, GPIO.OUT)
# Set logic levels
GPIO.output(PREHEAT_PIN, GPIO.HIGH)
GPIO.output(MICROWAVE_PIN, GPIO.HIGH)
GPIO.output(GRILL_PIN, GPIO.HIGH)
GPIO.output(CONVECTION_PIN, GPIO.HIGH)

###-> due to inverted logic of relay module, high logic is low and low logic is replaced with high logic level of gpio pins

# ------------------------------- LOGIC -------------------------------
preheat_sec = 0
microwave_sec = 0
convection_sec = 0
gril_sec = 0
flag = True


def update_timer(sec):
    t_min = int(sec / 60)
    t_sec = int(sec % 60)
    if t_min == 0 and t_sec < 2:
        timer_label1.config(text=(str(t_min) + " : " + str(t_sec)), fg="red")
    else:
        timer_label1.config(text=(str(t_min) + " : " + str(t_sec)), fg="green")


def start():
    global preheat_sec
    global microwave_sec
    global convection_sec
    global gril_sec
    global flag

    if not flag:
        flag = True
        start_btn.config(state="disabled")
        preheat()
        return  # other wise all other instruction also followed
    start_btn.config(state="disabled")
    preheat_sec = float(preheat_entry.get()) * 60
    microwave_sec = float(microwave_entry.get()) * 60
    convection_sec = float(convection_entry.get()) * 60
    gril_sec = float(gril_entry.get()) * 60
    preheat()


def stop():
    global flag
    flag = False
    start_btn.config(state="normal")
    timer_label1.config(text="--", fg="red")
    status_label1.config(text="Stopped by user", fg="red")

    # pull the pin to low logic state when stop pressed.
    GPIO.output(PREHEAT_PIN, GPIO.HIGH)
    GPIO.output(MICROWAVE_PIN, GPIO.HIGH)
    GPIO.output(GRILL_PIN, GPIO.HIGH)
    GPIO.output(CONVECTION_PIN, GPIO.HIGH)

def reset():
    global preheat_sec
    global microwave_sec
    global convection_sec
    global gril_sec
    global flag

    preheat_sec = 0
    microwave_sec = 0
    convection_sec = 0
    gril_sec = 0
    flag = True
    
    start_btn.config(state="normal")
    timer_label1.config(text="--", fg="red")
    status_label1.config(text="Reset by user", fg="red")

    # pull the pin to low logic state when reset pressed.
    GPIO.output(PREHEAT_PIN, GPIO.HIGH)
    GPIO.output(MICROWAVE_PIN, GPIO.HIGH)
    GPIO.output(GRILL_PIN, GPIO.HIGH)
    GPIO.output(CONVECTION_PIN, GPIO.HIGH)


def program_end():
    global flag
    start_btn.config(state="normal")
    status_label1.config(text="Dish Ready", fg="green")
    flag = True
    
def exitprog():
    reset()
    root.destroy()

def preheat():
    global preheat_sec
    global flag
    update_timer(preheat_sec)
    if not flag:
        return
    status_label1.config(text="Preheating Started", fg="red")
    # turn gpio on here
    GPIO.output(PREHEAT_PIN, GPIO.LOW)  # turn on preheat relay
    if preheat_sec > 0:
        preheat_sec -= 1
        root.after(delay_time, preheat)
    else:
        # turn gpio off here
        GPIO.output(PREHEAT_PIN, GPIO.HIGH)  # turn off preheat relay
        status_label1.config(text="Preheat Complete", fg="green")
        microwave()


def microwave():
    global microwave_sec
    global flag
    update_timer(microwave_sec)
    if not flag:
        return
    status_label1.config(text="Microwave Started", fg="red")
    # turn gpio on here
    GPIO.output(MICROWAVE_PIN, GPIO.LOW)  # turn on microwave relay
    if microwave_sec > 0:
        microwave_sec -= 1
        root.after(delay_time, microwave)
    else:
        # turn gpio off here
        GPIO.output(MICROWAVE_PIN, GPIO.HIGH)  # turn off microwave relay
        status_label1.config(text="Microwave Complete", fg="green")
        gril()


def gril():
    global gril_sec
    global flag
    update_timer(gril_sec)
    if not flag:
        return
    status_label1.config(text="Gril Started", fg="red")
    # turn gpio on here
    GPIO.output(GRILL_PIN, GPIO.LOW)  # turn on grill relay
    if gril_sec > 0:
        gril_sec -= 1
        root.after(delay_time, gril)
    else:
        # turn gpio off here
        GPIO.output(GRILL_PIN, GPIO.HIGH)  # turn off grill relay
        status_label1.config(text="Gril Complete", fg="green")
        convection()


def convection():
    global convection_sec
    global flag
    update_timer(convection_sec)
    if not flag:
        return
    status_label1.config(text="Convection Started", fg="red")
    # turn gpio on here
    GPIO.output(CONVECTION_PIN, GPIO.LOW)  # turn on convection relay
    if convection_sec > 0:
        convection_sec -= 1
        root.after(delay_time, convection)
    else:
        # turn gpio off here
        GPIO.output(CONVECTION_PIN, GPIO.HIGH)  # turn off convection relay
        status_label1.config(text="Convection Complete", fg="green")
        
        
        program_end()


    


# ----------------------------- END LOGIC -----------------------------

#################### Control Window
timeinfo_label = tk.Label(root, text="Time: ", font=FONT)
timeinfo_label.grid(row=0, column=0, padx=10, pady=10)
timer_label1 = tk.Label(root, text="--", font=FONT)
timer_label1.grid(row=0, column=1, padx=10, pady=10)

statusinfo_label = tk.Label(root, text="Current Status: ", font=FONT)
statusinfo_label.grid(row=1, column=0, padx=10, pady=10)
status_label1 = tk.Label(root, text="--", font=FONT)
status_label1.grid(row=1, column=1, padx=10, pady=10)

################### form

# Preheat
preheat_label = tk.Label(root, text="Preheat Minutes: ", font=FONT)
preheat_entry = tk.Entry(root, font=FONT)
preheat_label.grid(row=2, column=0, padx=10, pady=10)
preheat_entry.grid(row=2, column=1, padx=10, pady=10)

# Microwave
microwave_label = tk.Label(root, text="Microwave Minutes: ", font=FONT)
microwave_entry = tk.Entry(root, font=FONT)
microwave_label.grid(row=3, column=0, padx=10, pady=10)
microwave_entry.grid(row=3, column=1, padx=10, pady=10)
# Gril
gril_label = tk.Label(root, text="Gril Minutes: ", font=FONT)
gril_entry = tk.Entry(root, font=FONT)
gril_label.grid(row=4, column=0, padx=10, pady=10)
gril_entry.grid(row=4, column=1, padx=10, pady=10)

# convection
convection_label = tk.Label(root, text="Convection Minutes: ", font=FONT)
convection_entry = tk.Entry(root, font=FONT)
convection_label.grid(row=5, column=0, padx=10, pady=10)
convection_entry.grid(row=5, column=1, padx=10, pady=10)

start_btn = tk.Button(root, text="Start", font=FONT, command=start)
start_btn.grid(row=6, column=0)

stop_btn = tk.Button(root, text="Stop", font=FONT, command=stop)
stop_btn.grid(row=6, column=1)

reset_btn = tk.Button(root, text="Reset", font=FONT, command=reset)
reset_btn.grid(row=8, column=0)

exit_btn = tk.Button(root, text="Exit", font=FONT, command=exitprog)
exit_btn.grid(row=8, column=1)
# -----------------------------

root.mainloop()
