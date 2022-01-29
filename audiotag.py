import sys
import glob
import re
import mutagen
import sty
from pathlib import Path

# Show the full menu with descriptions
def show_full_menu():
  print("title - Change track titles")
  print("artist - Change track artists")
  print("album - Change track albums")
  print("genre - Change track genres")
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
    quit()
  
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
  for file in files:
    audio = mutagen.File(file)
    title = re.sub(r'[^\w ]', "", audio["title"][0]).lower()
    title = title.replace(" ", "_")
    tracknum = audio["tracknumber"][0]
    new_name = f"{tracknum}_{title}.flac"
    p = Path(file)
    p.rename(Path(p.parent, new_name))

# Show tracks to use as reference
# Show Track, Album, Genre, Title
# Use sty for coloring
def show_tracks():
  print("")
  for i, file in enumerate(files):
    audio = mutagen.File(file)
    artist = audio["artist"][0]
    album = audio["album"][0]
    genre = audio["genre"][0]
    title = audio["title"][0]
    index = i + 1
    
    print(f"{sty.fg.blue}Track:{sty.fg.rs} {index} | \
{sty.fg.blue}Artist:{sty.fg.rs} {artist} | \
{sty.fg.blue}Album:{sty.fg.rs} {album} | \
{sty.fg.blue}Genre:{sty.fg.rs} {genre} | \
{sty.fg.blue}Title:{sty.fg.rs} {title}")

# Fill missing data on Track, Artist, Album, Genre, and Title
def check_tracks():
  for file in files:
    audio = mutagen.File(file)
    do_update_track = False

    if "tracknumber" not in audio:
      audio["tracknumber"] = "1"
      do_update_track = True
    if "artist" not in audio or audio["artist"][0].strip() == "":
      audio["artist"] = "Unknown"
      do_update_track = True
    if "album" not in audio or audio["album"][0].strip() == "":
      audio["album"] = "Unknown"
      do_update_track = True  
    if "genre" not in audio or audio["genre"][0].strip() == "":
      audio["genre"] = "Unknown"
      do_update_track = True            
    if "title" not in audio or audio["title"][0].strip() == "":
      audio["title"] = Path(file).stem.strip()
      do_update_track = True

    if update_track:
      update_track(audio)

# Update track numbers based on the indexes of the files list
def update_tracknumbers():
  for i, file in enumerate(files):
    audio = mutagen.File(file)
    tracknum = audio["tracknumber"][0]
    n = str(i + 1)
    if tracknum != n:
      audio["tracknumber"] = n
      update_track(audio)

# Save track data and show feedback
def update_track(audio):
  title = audio["title"][0]
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
  audio = mutagen.File(files[index])
  audio[field] = value
  update_track(audio)

# Sort by tracknumber data
def initial_sort():
  global files
  files = sorted(files, key=lambda x: int(mutagen.File(x)["tracknumber"][0]))

# Main function
def main() -> None:
  global files
  files = glob.glob(f"{sys.argv[1]}/*.flac")
  check_tracks()
  initial_sort()
  update_tracknumbers()

  while True:
    show_tracks()
    show_menu()  

if __name__ == "__main__":
  main()  