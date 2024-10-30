import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from youtubesearchpython import VideosSearch
import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk, ImageDraw
import yt_dlp as youtube_dl
import vlc
import time
import logging

logging.basicConfig(level=logging.DEBUG)

CLIENT_ID = 'f7011cc9be6b498da0866a3a8a697956'
CLIENT_SECRET = '26189f7419c64ba58ca2f8ab83e7300a'

auth_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
sp = spotipy.Spotify(auth_manager=auth_manager)

playlist = []
current_player = None

def search_spotify(query):
    results = sp.search(q=query, type='track', limit=1)
    if results['tracks']['items']:
        track = results['tracks']['items'][0]
        track_info = {
            'name': track['name'],
            'artist': track['artists'][0]['name'],
            'url': track['external_urls']['spotify']
        }
        return track_info
    else:
        return None

def search_youtube(track_name, artist_name):
    search_query = f"{track_name} {artist_name} audio"
    videos_search = VideosSearch(search_query, limit=1)
    result = videos_search.result()
    if result['result']:
        video_url = f"https://www.youtube.com/watch?v={result['result'][0]['id']}"
        return video_url
    else:
        return None

def play_song(track_info=None):
    global current_player
    if current_player:
        current_player.stop()

    if track_info is None:
        query = song_entry.get()
        if not query:
            messagebox.showwarning("Input Error", "Please enter a song name.")
            return
        track_info = search_spotify(query)

    if track_info:
        track_label.config(text=f"{track_info['name']} by {track_info['artist']}", fg="red", font=("Roboto", 18, "bold"))
        youtube_url = search_youtube(track_info['name'], track_info['artist'])
        if youtube_url:
            try:
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                }
                with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(youtube_url, download=False)
                    play_url = info['url']

                instance = vlc.Instance()
                player = instance.media_player_new()
                media = instance.media_new(play_url)
                media.get_mrl()
                player.set_media(media)
                
                # Set the volume (0-100)
                player.audio_set_volume(volume_scale.get())
                
                player.play()
                
                
                time.sleep(1)
                
                if player.is_playing():
                    logging.info("Player is playing")
                else:
                    logging.warning("Player is not playing after start command")

                current_player = player
            except Exception as e:
                logging.error(f"Error playing song: {str(e)}")
                messagebox.showerror("Error", f"Error playing song. Please try another song.")
        else:
            messagebox.showerror("Error", "Couldn't find the song on YouTube.")
    else:
        messagebox.showerror("Error", "Couldn't find the song on Spotify.")
        track_label.config(text="")

def add_to_playlist():
    query = song_entry.get()
    if not query:
        messagebox.showwarning("Input Error", "Please enter a song name.")
        return

    track_info = search_spotify(query)
    if track_info:
        playlist.append(track_info)
        update_playlist_display()
        messagebox.showinfo("Success", f"Added '{track_info['name']}' to the playlist.")
    else:
        messagebox.showerror("Error", "Couldn't find the song on Spotify.")

def remove_from_playlist():
    selection = playlist_tree.selection()
    if selection:
        index = int(playlist_tree.index(selection[0]))
        removed_song = playlist.pop(index)
        update_playlist_display()
        messagebox.showinfo("Success", f"Removed '{removed_song['name']}' from the playlist.")
    else:
        messagebox.showwarning("Selection Error", "Please select a song to remove.")

def update_playlist_display():
    playlist_tree.delete(*playlist_tree.get_children())
    for i, track in enumerate(playlist):
        playlist_tree.insert("", "end", values=(i+1, track['name'], track['artist']))

def play_selected_song():
    selection = playlist_tree.selection()
    if selection:
        index = int(playlist_tree.index(selection[0]))
        play_song(playlist[index])
    else:
        messagebox.showwarning("Selection Error", "Please select a song to play.")

def fullscreen_toggle(event=None):
    global fullscreen
    fullscreen = not fullscreen
    app.attributes("-fullscreen", fullscreen)
    if not fullscreen:
        app.geometry("1024x768")

def exit_fullscreen(event=None):
    global fullscreen
    fullscreen = False
    app.attributes("-fullscreen", False)
    app.geometry("1024x768")

def rounded_rectangle_image(size, color, radius):
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle([0, 0, size[0], size[1]], radius, fill=color)
    return ImageTk.PhotoImage(img)

app = tk.Tk()
app.title("Modern Music Player with Playlist")

fullscreen = True
app.attributes("-fullscreen", True)

try:
    background_image = Image.open("28.jpg")
    bg_width, bg_height = app.winfo_screenwidth(), app.winfo_screenheight()
    background_image = background_image.resize((bg_width, bg_height), Image.LANCZOS)
    background_photo = ImageTk.PhotoImage(background_image)

    canvas = tk.Canvas(app, width=bg_width, height=bg_height, highlightthickness=0)
    canvas.pack(fill="both", expand=True)
    canvas.create_image(0, 0, image=background_photo, anchor="nw")

except Exception as e:
    print(f"Error loading background image: {e}")

def create_rounded_button(master, text, command, width=150):
    button_image = rounded_rectangle_image((width, 50), "#58D68D", 25)
    button = tk.Label(master, text=text, font=("Roboto", 16), fg="white", bd=0, bg="#58D68D", image=button_image, compound="center")
    button.bind("<Button-1>", lambda event: command())
    button.image = button_image
    return button

def create_rounded_entry(master):
    entry_image = rounded_rectangle_image((350, 40), "#F0F3F4", 20)
    entry_canvas = tk.Canvas(master, width=350, height=40, highlightthickness=0, bg=canvas["bg"])
    entry_canvas.create_image(175, 20, image=entry_image)
    entry_canvas.image = entry_image
    entry = tk.Entry(master, font=("Roboto", 14), width=30, bd=0, bg="#F0F3F4", highlightthickness=0, relief="flat")
    entry_canvas.create_window(175, 20, window=entry)
    return entry_canvas, entry

entry_canvas, song_entry = create_rounded_entry(app)
canvas.create_window(bg_width/2, bg_height/2 - 100, window=entry_canvas)

play_button = create_rounded_button(app, "Play", play_song)
canvas.create_window(bg_width/2 - 240, bg_height/2, window=play_button)

add_button = create_rounded_button(app, "Add to Playlist", add_to_playlist)
canvas.create_window(bg_width/2, bg_height/2, window=add_button)

remove_button = create_rounded_button(app, "Remove from Playlist", remove_from_playlist, width=200)
canvas.create_window(bg_width/2 + 240, bg_height/2, window=remove_button)

track_label = tk.Label(app, text="", font=("Roboto", 18, "bold"), fg="#ECF0F1", bg=canvas["bg"])
canvas.create_window(bg_width/2, bg_height/2 + 100, window=track_label)


playlist_frame = tk.Frame(app, bg=canvas["bg"])
canvas.create_window(bg_width/2, bg_height/2 + 200, window=playlist_frame)


playlist_tree = ttk.Treeview(playlist_frame, columns=("No.", "Song", "Artist"), show="headings", height=10)
playlist_tree.heading("No.", text="No.")
playlist_tree.heading("Song", text="Song")
playlist_tree.heading("Artist", text="Artist")
playlist_tree.column("No.", width=50)
playlist_tree.column("Song", width=200)
playlist_tree.column("Artist", width=150)
playlist_tree.pack(side="left")


scrollbar = ttk.Scrollbar(playlist_frame, orient="vertical", command=playlist_tree.yview)
scrollbar.pack(side="right", fill="y")
playlist_tree.configure(yscrollcommand=scrollbar.set)


playlist_tree.bind("<Double-1>", lambda event: play_selected_song())

def enter_key_pressed(event):
    play_song()

song_entry.bind("<Return>", enter_key_pressed)

app.bind("<F11>", fullscreen_toggle)
app.bind("<Escape>", exit_fullscreen)


volume_label = tk.Label(app, text="Volume:", font=("Roboto", 14), fg="white", bg=canvas["bg"])
canvas.create_window(bg_width/2 - 100, bg_height - 50, window=volume_label)

volume_scale = tk.Scale(app, from_=0, to=100, orient=tk.HORIZONTAL, length=200, bg=canvas["bg"], highlightthickness=0)
volume_scale.set(50)
canvas.create_window(bg_width/2 + 50, bg_height - 50, window=volume_scale)

def update_volume(event=None):
    if current_player:
        current_player.audio_set_volume(volume_scale.get())

volume_scale.bind("<ButtonRelease-1>", update_volume)

app.mainloop()