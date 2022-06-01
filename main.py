
from tkinter import *
from tkinter import ttk
from PIL import Image, ImageTk, ImageFilter

import requests
import os
current_directory = os.path.dirname(__file__)
os.chdir(current_directory)

from pyautogui import press
from spotify_playback import refresh_token, update_playback_info, fetched_song_info


# ================================= Window Initiation

mw = Tk()
mw.title("Visualizer")
scale = 1 # between 0.5 and 1
# if equal to 1, window becomes fullscreen (recommended)
mw_width, mw_height = int(scale*mw.winfo_screenwidth()), int(scale*mw.winfo_screenheight())
mw.minsize(mw_width, mw_height)
mw.resizable(False, False)
mw.attributes("-fullscreen", bool(int(scale))) # sets fullscreen
if scale==1: mw.config(cursor="none") # hides the mouse
mw.iconbitmap(default="./icon.ico") # changes window icon


# ====================================== Global Variables

previous_album_title = StringVar()
previous_album_title.set(" _NONE_ ")
# checks if album title has changed, so that the artwork can be updated
# this is necessary to avoid downloading a new image every API fetch (every 2 seconds)

previous_track_was_ad = BooleanVar()
previous_track_was_ad.set(False)
# checks if previous track was an add, so that speakers can be unmuted
# this is necessary to avoid unmuting every API fetch (every 2 seconds)


# ===============================================
def place_and_blur(new_center_image):

    # takes in PIL.Image object and lays it out with blured background of the same image

    global bg_image, shadow_image, artwork_image
    global bg_instance, shadow_instance, artwork_instance

    main_canvas.delete(bg_instance)
    main_canvas.delete(shadow_instance)
    main_canvas.delete(artwork_instance)

    bg_image = new_center_image.resize((mw_width, mw_width), resample=0)
    bg_image = bg_image.filter(ImageFilter.GaussianBlur(20))
    bg_image = ImageTk.PhotoImage(bg_image)

    artwork_image = ImageTk.PhotoImage(new_center_image)
        
    bg_instance = main_canvas.create_image(0, 0, anchor=NW, image=bg_image)
    shadow_instance = main_canvas.create_image(mw_width//2, mw_height//2, anchor=CENTER, image=shadow_image)
    artwork_instance = main_canvas.create_image(mw_width//2, mw_height//2, anchor=CENTER, image=artwork_image)

def download_image(image_url, save_path):

    # downloads image from the internet and saves it in given path
    # path must include image file name at the end
    response = requests.get(image_url)
    with open(save_path, "wb") as f:
        f.write(response.content)

# ========================================= Window States
# These functions modify the running window according to specific states

def expired_token_state():

    place_and_blur(Image.open("./pictures/loading.png"))
    previous_album_title.set(" _NONE_ ")
    refresh_token()
    update_playback_info()

def no_internet_state():

    place_and_blur(Image.open("./pictures/no_internet.png"))
    previous_album_title.set(" _NONE_ ")

def spotify_closed_state():

    place_and_blur(Image.open("./pictures/not_playing.png"))
    previous_album_title.set(" _NONE_ ")

def advertisement_state():

    place_and_blur(Image.open("./pictures/muted.png"))
    previous_album_title.set(" _NONE_ ")

    previous_track_was_ad.set(True)
    mute_speaker()

def normal_playback_state():

    song_info = fetched_song_info()

    track_title = song_info["item"]["name"]
    artist_list = ", ".join(artist["name"] for artist in song_info["item"]["artists"])
    album_title = song_info["item"]["album"]["name"]
    artwork_url = song_info["item"]["album"]["images"][0]["url"]

    if album_title != previous_album_title.get(): # new album => artwork needs changing

        previous_album_title.set(album_title)

        print("Downloading new album artowrk...", end="\r")
        download_image(artwork_url, "./pictures/artwork.png")
        print("New album artwork downloaded.")

        place_and_blur(Image.open("./pictures/artwork.png"))

        global progress_instance

    if previous_track_was_ad.get()==True:

        previous_track_was_ad.set(False)
        unmute_speaker()

    progress_percentage = int(100*(song_info["progress_ms"]/song_info["item"]["duration_ms"]))
    main_canvas.tag_raise(progress_instance) # this moves progress_instance to top layer so it can be seen
    main_canvas.moveto(progress_instance, 19*progress_percentage - mw_width + 20, mw_height - 5) # moves progress_bar to match song progress


# ====================================== Main Loop Function
def mainloop_function():

    os.system("cls")

    update_playback_info()
    song_info = fetched_song_info() # json object, refer to spotify_playback.py


    if len(song_info) < 2: # didn't receive song info

        if song_info["error_message"]=="expired_token":
            expired_token_state()
            
        elif song_info["error_message"]=="no_internet":
            no_internet_state()
            
        elif song_info["error_message"]=="not_playing":
            spotify_closed_state()
            
        elif song_info["error_message"]=="ad":
            advertisement_state()

    else: # succesfully got song info

        normal_playback_state()


    # runs mainloop_function every 2 seconds
    # sleep label is a dummy label
    sleep_label.after(2000, mainloop_function)


# ====================================== Keybinds
def right_arrow_event(event):
    press("nexttrack")

def left_arrow_event(event):
    press("prevtrack")

def escape_event(event):
    mw.destroy()

def space_event(event):
    press("playpause")


mw.bind("<Escape>", escape_event)
mw.bind("<space>", space_event)
mw.bind("<Right>", right_arrow_event)
mw.bind("<Left>", left_arrow_event)

def unmute_speaker():

    press("volumedown")
    press("volumeup")

def mute_speaker():

    unmute_speaker()
    press("volumemute")

# ====================================== Frames - Widgets - Buttons

sleep_label = Label(mw) # dummy label

# creating the canvas on which all images will be placed
main_canvas = Canvas(mw, width=1920, height=1920, bd=0, highlightthickness=0)
main_canvas.place(x=0, y=0)

# creating image instances
bg_image = ImageTk.PhotoImage(Image.open("./pictures/starting_bg.png"))
shadow_image = ImageTk.PhotoImage(Image.open("./pictures/shadow.png"))
artwork_image = ImageTk.PhotoImage(Image.open("./pictures/loading.png"))
progress_image = ImageTk.PhotoImage(Image.open("./pictures/progress_bar.png"))

# placing images on canvas
bg_instance = main_canvas.create_image(0, 0, anchor=NW, image=bg_image)
shadow_instance = main_canvas.create_image(mw_width//2, mw_height//2, anchor=CENTER, image=shadow_image)
artwork_instance = main_canvas.create_image(mw_width//2, mw_height//2, anchor=CENTER, image=artwork_image)
progress_instance = main_canvas.create_image(-1940, mw_height - 5, anchor=NW, image=progress_image)

# ==========================================
mainloop_function()
mw.mainloop()