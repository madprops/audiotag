import sys
import glob
import re
import sty
from pathlib import Path
from mutagen.flac import FLAC
from mutagen.oggvorbis import OggVorbis
from mutagen.easyid3 import EasyID3

# Show the full menu with descriptions
def show_full_menu():
  print("artist - Change track artists")
  print("album - Change track albums")
  print("genre - Change track genres")
  print("title - Change track titles")
  print("move - Move track to a new position")
  print("rename - Apply filename changes")
  print("help - Show this message")
  print("exit - Exit the application")

# Show a simple menu without descriptions
def show_simple_menu(): 
  print("artist | album | genre | title | move | rename | help | exit")

# Show the menu and wait for input
def show_menu(full_menu = False):
  print("")

  if full_menu:
    show_full_menu()
  else:
    show_simple_menu()

  ans = input("> ")

  if ans == "title" or ans == "artist" or ans == "album" or ans == "genre":
    change_value(ans)      

  elif ans == "move":
    move_track()
  
  elif ans == "rename":
    rename_files()
  
  elif ans == "help":
    show_menu(True)
  
  elif ans == "exit":
    quit()

# Move track positions by selecting 2 indexes
def move_track():
  n1 = int(input("Track Number: "))
  n2 = int(input("New Track Number: "))

  if n1 <= 0 or n1 > len(files):
    return
  
  if n2 <= 0:
    n2 = 1
  
  if n2 > len(files):
    n2 = len(files)

  change_index(n1 - 1, n2 - 1)
  update_tracknumbers()

# Generic function to change one or more values
def change_value(prop):
  w = prop.capitalize()
  ans = input("Target (#, all): ")
  if ans.isnumeric():
    n = int(ans)
    if n <= 0 or n > len(files):
      return
    t = input(f"New {w}: ")
    changeone(n - 1, prop, t)
  elif ans == "all":
    a = input(f"New {w}: ")
    changeall(prop, a)  

# Rename all file names based on tags
# Syntax: {tracknumber}_{the_title}
def rename_files():
  ans = input("Rename files? (y/n): ")

  if ans == "y":
    for file in files:
      p = Path(file)
      audio = get_audio_object(file)
      title = re.sub(r'[^\w ]', "", get_tag(audio, "title")).lower()
      title = title.replace(" ", "_")
      tracknum = get_tag(audio, "tracknumber")
      new_name = f"{tracknum}_{title}{p.suffix}"
      p.rename(Path(p.parent, new_name))

    startup()

# Show tracks to use as reference
# Show Track, Artist, Album, Genre, Title
# Use sty for coloring
def show_tracks():
  print("")
  for i, file in enumerate(files):
    audio = get_audio_object(file)
    artist = get_tag(audio, "artist")
    album = get_tag(audio, "album")
    genre = get_tag(audio, "genre")
    title = get_tag(audio, "title")
    index = i + 1
    
    print(f"{sty.fg.blue}Track:{sty.fg.rs} {index} | \
{sty.fg.blue}Artist:{sty.fg.rs} {artist} | \
{sty.fg.blue}Album:{sty.fg.rs} {album} | \
{sty.fg.blue}Genre:{sty.fg.rs} {genre} | \
{sty.fg.blue}Title:{sty.fg.rs} {title}")

# Fill missing data on Track, Artist, Album, Genre, and Title
def check_tracks():
  for file in files:
    audio = get_audio_object(file)
    set_tag_if_empty(audio, "tracknumber", "1")
    set_tag_if_empty(audio, "artist", "Unknown")
    set_tag_if_empty(audio, "album", "Unknown")
    set_tag_if_empty(audio, "genre", "Unknown")
    set_tag_if_empty(audio, "title", "Unknown")

# If value is empty fill it with a value
def set_tag_if_empty(audio, field, value):
  if get_tag(audio, field) == "":
    set_tag(audio, field, value)
    update_track(audio)

# Update track numbers based on the indexes of the files list
def update_tracknumbers():
  for i, file in enumerate(files):
    audio = get_audio_object(file)
    tracknum = get_tag(audio, "tracknumber")
    n = str(i + 1)
    if tracknum != n:
      set_tag(audio, "tracknumber", n)
      update_track(audio)

# Save track data and show feedback
def update_track(audio):
  title = get_tag(audio, "title")
  print(f"Updating track: {title}")
  audio.save()

# Change the index of a list item
def change_index(old_index, new_index):
  files.insert(new_index, files.pop(old_index))

# Change a field on all tracks
def changeall(field, value):
  for i, file in enumerate(files):
    changeone(i, field, value)

# Change a field on a specific track
def changeone(index, field, value):
  file = files[index]
  audio = get_audio_object(file)
  set_tag(audio, field, value)
  update_track(audio)

# Get proper audio object
def get_audio_object(file):
  p = Path(file)
  if p.suffix == ".mp3":
    return EasyID3(file)
  elif p.suffix == ".flac":
    return FLAC(file)
  elif p.suffix == ".ogg":
    return OggVorbis(file)

# Get tag from an audio object
# Return empty string if non existent
def get_tag(audio, tag):
  if tag in audio:
    return audio[tag][0].strip()
  else:
    return ""

# Set a tag from an audio object
def set_tag(audio, tag, value):
  audio[tag] = [value]

# Sort by tracknumber once at startup
def initial_sort():
  global files
  files = sorted(files, key=lambda x: int(get_tag(get_audio_object(x), "tracknumber")))

# Get audio files
def get_files():
  global files
  flacs = glob.glob(f"{sys.argv[1]}/*.flac")
  ogg = glob.glob(f"{sys.argv[1]}/*.ogg")
  mp3 = glob.glob(f"{sys.argv[1]}/*.mp3")
  files = flacs + ogg + mp3
  if len(files) == 0:
    print("No files found")
    quit()

# Get and prepare files
def startup():
  get_files()
  check_tracks()
  initial_sort()
  update_tracknumbers()  

# Main function
def main() -> None:
  startup()

  while True:
    show_tracks()
    show_menu()  

if __name__ == "__main__":
  main()  