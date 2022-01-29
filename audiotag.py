import sys
import glob
import re
import sty
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
def spacer():
  print("")

# Show info messages
def show_info(header, message):
  print(f"{sty.fg.green}{header}:{sty.fg.rs} {message}")

# Show a simple menu without descriptions
def show_simple_menu():
  print(" | ".join(command_list()))

# Show the menu and wait for input
def show_menu(full_menu = False):
  if full_menu:
    show_full_menu()
  else:
    spacer()
    show_simple_menu()

  ans = input("> ").strip()
  if ans == "": return
  spacer()

  args = list(filter(lambda x: x != "", ans.split(" ")))
  a1 = args[1] if len(args) > 1 else ""

  if args[0] == "title" or args[0] == "artist" or args[0] == "album" or args[0] == "genre":
    change_value(args[0], a1)

  elif args[0] == "move":
    move_track()

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
        update_track(audio, False)
        show_info("Cleaned", f"{title} to {new_title}")

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
def change_value(prop, ans):
  w = prop.capitalize()

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
        show_info("Renamed", f"{old_name} to {new_name}")

    startup()

# Show tracks to use as reference
# Show Track, Artist, Album, Genre, Title
# Use sty for coloring
def show_tracks():
  spacer()

  for i, file in enumerate(files):
    audio = get_audio_object(file)
    artist = get_tag(audio, "artist")
    album = get_tag(audio, "album")
    genre = get_tag(audio, "genre")
    title = get_tag(audio, "title")
    index = i + 1

    print(f"\
{sty.fg.blue}#{sty.fg.rs} {index} | \
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
def update_track(audio, feedback = True):
  title = get_tag(audio, "title")
  audio.save()
  if feedback:
    show_info("Updated", title)

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