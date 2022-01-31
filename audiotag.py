# Std imports
import sys
import glob
import re
import signal
from pathlib import Path

# Pip installs
import sty
from mutagen.flac import FLAC
from mutagen.oggvorbis import OggVorbis
from mutagen.easyid3 import EasyID3

# Available commands and their description
commands = [
  ["artist", "Change track artists"],
  ["album", "Change track albums"],
  ["title", "Change track titles"],
  ["move", "Move track to a new position"],
  ["rename", "Apply filename changes"],
  ["clean", "Clean track titles"],
  ["reload", "Reload files"],
  ["help", "Show this message"],
  ["exit", "Exit the application"]
]

# Get commands list
def command_list():
  return [cmd[0] for cmd in commands]

# Show the full menu with descriptions
def show_full_menu():
  max_cmd = len(max(command_list(), key = len))
  for cmd in commands:
    c = cmd[0].ljust(max_cmd, " ")
    echo(f"{c} - {cmd[1]}")

# Simple space
def space():
  print("")

# Normal print
def echo(s, spaced = True):
  if spaced:
    space()
  print(s)

# Get input from the user
def prompt(s):
  print("")
  return input(s).strip()

# Show info messages
def show_info(header, message):
  echo(f"{sty.fg.green}{header}:{sty.fg.rs} {message}")

# Show action
def show_action(message):
  echo(f"{sty.fg.green}{message}{sty.fg.rs}")

# Show error
def show_error(message):
  echo(f"{sty.fg.red}{message}{sty.fg.rs}")

# Quit program
def do_quit():
  space()
  quit()

# Show a simple menu without descriptions
def show_simple_menu():
  echo(" | ".join(command_list()))

# Show the menu and wait for input
def show_menu(full_menu = False):
  if full_menu:
    show_full_menu()
  else:
    show_simple_menu()

  ans = prompt("> ")
  if ans == "": return

  args = list(filter(lambda x: x != "", ans.split(" ")))
  tail = " ".join(args[1:]) if len(args) > 1 else ""

  if args[0] == "title" or args[0] == "artist" or args[0] == "album":
    change_value(args[0], tail)

  elif args[0] == "move":
    move_track(tail)

  elif args[0] == "rename":
    rename_files(tail)

  elif args[0] == "clean":
    clean_titles(tail)
  
  elif args[0] == "reload":
    reload_files()

  elif args[0] == "help":
    show_menu(True)

  elif args[0] == "exit":
    quit()

# Clean titles using some basic rules
def clean_titles(ans):
  targets = get_targets(ans)

  for num in targets:
    file = files[num - 1]
    p = Path(file)
    audio = get_audio_object(file)
    title = get_tag(audio, "title")
    new_title = title.replace("_", " ").title()
    if title != new_title:
      set_tag(audio, "title", new_title)

# Reload files
def reload_files(force = False):
  if not force:
    ans = prompt("Reload files? (y/n): ")
  else:
    ans = "y"
  if ans == "y":
    startup()
    show_action("Files were reloaded.")  

# Move track positions by selecting 2 indexes
def move_track(n1):
  if len(files) == 1:
    n2 = prompt("New Track Number: ")
    set_tag(get_audio_object(files[0]), "tracknumber", n2)
    return

  if n1 == "":
    n1 = prompt("Track Number: ")
  n1 = int(n1)

  n2 = int(prompt("New Track Number: "))

  if n1 <= 0 or n1 > len(files):
    return

  if n2 <= 0:
    n2 = 1

  if n2 > len(files):
    n2 = len(files)

  change_index(n1 - 1, n2 - 1)
  update_tracknumbers()

# Get track targets
def get_targets(ans):
  if len(files) == 1:
    return [1]

  if ans == "":
    ans = prompt("Target ( # | all | n1-n2 | n1,n2 ): ")

  if ans.isnumeric():
    n = int(ans)
    if n <= 0 or n > len(files):
      return []
    targets = [n]

  elif ans == "all":
    targets = range(1, len(files) + 1)
  
  elif "-" in ans and "," not in ans:
    nums = list(map(lambda x: int(x.strip()), ans.split("-")))
    
    if len(nums) != 2:
      return []

    if nums[0] >= nums[1]: return []
    if nums[0] <= 0: return []
    if nums[1] > len(files): return []
    targets = range(nums[0], nums[1] + 1)

  elif "," in ans:
    nums = list(map(lambda x: int(x.strip()), ans.split(",")))
    
    if len(nums) == 0 or len(nums) > len(files):
      return []
    
    for num in nums:
      if num <= 0 or num > len(files):
        return []

    targets = nums
  
  else:
    targets = []

  return targets

# Generic function to change one or more values
def change_value(prop, ans):
  targets = get_targets(ans)
  
  if len(targets) > 0:
    w = prop.capitalize()
    new_value = prompt(f"New {w}: ").strip()
    change_set(targets, prop, new_value)

# Rename file names based on tags
# Syntax: {tracknumber}_{the_title}
def rename_files(ans):
  targets = get_targets(ans)
  renamed = False

  for num in targets:
    file = files[num - 1]
    p = Path(file)
    audio = get_audio_object(file)
    title = re.sub(r'[^\w ]', "", get_tag(audio, "title")).lower()
    title = title.replace(" ", "_")
    tracknum = get_tag(audio, "tracknumber")
    new_name = f"{tracknum}_{title}{p.suffix}"
    old_name = p.name
    if p.name != new_name:
      new_path = Path(p.parent, new_name)
      p.rename(new_path)
      if filesmode == "file":
        filespath = new_path
      show_info("Rename", f"{old_name} {sty.fg.blue}to{sty.fg.rs} {new_name}")
      renamed = True
  
  if renamed:
    reload_files(True)

# Show tracks to use as reference
# Show Track, Artist, Album, Title
# Use sty for coloring
def show_tracks():
  space()

  tracks = []
  artists = []
  albums = []
  titles = []

  for i, file in enumerate(files):
    audio = get_audio_object(file)
    tracks.append(get_tag(audio, "tracknumber"))
    artists.append(get_tag(audio, "artist"))
    albums.append(get_tag(audio, "album"))
    titles.append(get_tag(audio, "title"))

  max_track = len(max(tracks, key = len))
  max_artist = len(max(artists, key = len))
  max_album = len(max(albums, key = len))

  for i, file in enumerate(files):
    text = ""

    track = tracks[i].ljust(max_track, " ")
    text += f"{sty.fg.blue}#{sty.fg.rs} {track} | "

    artist = artists[i].ljust(max_artist, " ")
    text += f"{sty.fg.blue}Artist:{sty.fg.rs} {artist} | "

    album = albums[i].ljust(max_album, " ")
    text += f"{sty.fg.blue}Album:{sty.fg.rs} {album} | "

    text += f"{sty.fg.blue}Title:{sty.fg.rs} {titles[i]}"

    echo(text, False)

# Fill missing data on Track, Artist, Album, Title
def check_tracks():
  for file in files:
    set_tag_if_empty(file, "tracknumber", "1")
    set_tag_if_empty(file, "artist", "Unknown")
    set_tag_if_empty(file, "album", "Unknown")
    set_tag_if_empty(file, "title", Path(file).stem)

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
def change_set(nums, field, value):
  for num in nums:
    change_one(num - 1, field, value)

# Change a field on a specific track
def change_one(index, field, value):
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

# Get proper tracknumber
def clean_tracknumber(s):
  return int(re.search("[0-9]+", s).group())

# Sort by tracknumber once at startup
def initial_sort():
  global files
  files = sorted(files, key=lambda x: clean_tracknumber(get_tag(get_audio_object(x), "tracknumber")))

# Get audio files
def get_files():
  global files
  global filesmode
  files = []
  p = Path(filespath)
  if p.is_dir():
    filesmode = "dir"
    flacs = glob.glob(f"{filespath}/*.flac")
    ogg = glob.glob(f"{filespath}/*.ogg")
    mp3 = glob.glob(f"{filespath}/*.mp3")
    files = flacs + ogg + mp3
  elif p.is_file():
    filesmode = "file"
    files = [str(p)]
  if len(files) == 0:
    show_error("No files found.")
    do_quit()

# Get and prepare files
def startup():
  get_files()
  check_tracks()
  initial_sort()
  update_tracknumbers()

# Main function
def main() -> None:
  global filespath
  filespath = sys.argv[1]
  signal.signal(signal.SIGINT, lambda x, y: sys.exit(0))

  startup()

  while True:
    show_tracks()
    show_menu()

if __name__ == "__main__":
  main()