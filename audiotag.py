import sys
import glob
import re
import sty
import signal
from pathlib import Path
from mutagen.flac import FLAC
from mutagen.oggvorbis import OggVorbis
from mutagen.easyid3 import EasyID3

# Available commands and their description
commands = [
  ["artist", "Change track artists"],
  ["album", "Change track albums"],
  ["genre", "Change track genres"],
  ["title", "Change track titles"],
  ["move", "Move track to a new position"],
  ["rename", "Apply filename changes"],
  ["clean", "Clean track titles"],
  ["help", "Show this message"],
  ["exit", "Exit the application"]
]

# Get commands list
def command_list():
  return [cmd[0] for cmd in commands]

# Show the full menu with descriptions
def show_full_menu():
  for cmd in commands:
    print(f"{cmd[0]} - {cmd[1]}")

# Simple space
def space():
  print("")

# Show info messages
def show_info(header, message):
  space()
  print(f"{sty.fg.green}{header}:{sty.fg.rs} {message}")

# Show a simple menu without descriptions
def show_simple_menu():
  print(" | ".join(command_list()))

# Show the menu and wait for input
def show_menu(full_menu = False):
  if full_menu:
    show_full_menu()
  else:
    space()
    show_simple_menu()

  space()
  ans = input("> ").strip()
  if ans == "": return
  space()

  args = list(filter(lambda x: x != "", ans.split(" ")))
  a1 = args[1] if len(args) > 1 else ""

  if args[0] == "title" or args[0] == "artist" or args[0] == "album" or args[0] == "genre":
    change_value(args[0], a1)

  elif args[0] == "move":
    move_track(a1)

  elif args[0] == "rename":
    rename_files()

  elif args[0] == "clean":
    clean_titles()

  elif args[0] == "help":
    show_menu(True)

  elif args[0] == "exit":
    quit()

# Clean titles using some basic rules
def clean_titles():
  ans = input("Clean titles? (y/n): ")

  if ans == "y":
    for file in files:
      audio = get_audio_object(file)
      title = get_tag(audio, "title")
      new_title = title.replace("_", " ").title()
      if title != new_title:
        set_tag(audio, "title", new_title)

# Move track positions by selecting 2 indexes
def move_track(n1):
  if len(files) == 1:
    n2 = input("New Track Number: ")
    set_tag(get_audio_object(files[0]), "tracknumber", n2)
    return
  
  if n1 == "":
    n1 = input("Track Number: ")
  n1 = int(n1)

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
def change_value(prop, ans):
  w = prop.capitalize()

  if len(files) == 1:
    t = input(f"New {w}: ")
    changeone(0, prop, t)
    return

  if ans == "": 
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
      old_name = p.name
      if p.name != new_name:
        p.rename(Path(p.parent, new_name))
        show_info("Rename", f"{old_name} to {new_name}")

    startup()

# Show tracks to use as reference
# Show Track, Artist, Album, Genre, Title
# Use sty for coloring
def show_tracks():
  space()

  for i, file in enumerate(files):
    audio = get_audio_object(file)
    track = get_tag(audio, "tracknumber")
    artist = get_tag(audio, "artist")
    album = get_tag(audio, "album")
    genre = get_tag(audio, "genre")
    title = get_tag(audio, "title")

    print(f"\
{sty.fg.blue}#{sty.fg.rs} {track} | \
{sty.fg.blue}Artist:{sty.fg.rs} {artist} | \
{sty.fg.blue}Album:{sty.fg.rs} {album} | \
{sty.fg.blue}Genre:{sty.fg.rs} {genre} | \
{sty.fg.blue}Title:{sty.fg.rs} {title}")

# Fill missing data on Track, Artist, Album, Genre, and Title
def check_tracks():
  for file in files:
    set_tag_if_empty(file, "tracknumber", "1")
    set_tag_if_empty(file, "artist", "Unknown")
    set_tag_if_empty(file, "album", "Unknown")
    set_tag_if_empty(file, "genre", "Unknown")
    set_tag_if_empty(file, "title", "Unknown")

# If value is empty fill it with a value
def set_tag_if_empty(file, field, value):
  audio = get_audio_object(file)
  if get_tag(audio, field) == "":
    set_tag(audio, field, value)

# Update track numbers based on the indexes of the files list
def update_tracknumbers():
  if len(files) == 1: return

  for i, file in enumerate(files):
    audio = get_audio_object(file)
    tracknum = get_tag(audio, "tracknumber")
    n = str(i + 1)
    if tracknum != n:
      set_tag(audio, "tracknumber", n)

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
  audio.save()
  show_info("Update", f"{sty.fg.blue}{tag}{sty.fg.rs} set to {sty.fg.blue}{value}{sty.fg.rs} in {Path(audio.filename).name}")

# Sort by tracknumber once at startup
def initial_sort():
  global files
  files = sorted(files, key=lambda x: int(get_tag(get_audio_object(x), "tracknumber")))

# Get audio files
def get_files():
  global files
  filespath = sys.argv[1]
  p = Path(filespath)
  if p.is_dir():
    flacs = glob.glob(f"{filespath}/*.flac")
    ogg = glob.glob(f"{filespath}/*.ogg")
    mp3 = glob.glob(f"{filespath}/*.mp3")
    files = flacs + ogg + mp3
  elif p.is_file():
    files = [str(p)]
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
  signal.signal(signal.SIGINT, lambda x, y: sys.exit(0))

  startup()

  while True:
    show_tracks()
    show_menu()

if __name__ == "__main__":
  main()