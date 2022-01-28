import sys
import glob
import re
from pathlib import Path
from mutagen.flac import FLAC

def show_menu():
  print("")
  print("move - Move track to a new position")
  print("rename - Apply filename changes")

  ans = input("> ")

  if ans == "move":
    n1 = int(input("Track Number: "))
    n2 = int(input("New Track Number: "))

    if n1 <= 0 or n1 > len(files):
      return
    
    if n2 <= 0:
      n2 = 1
    
    if n2 > len(files):
      n2 = len(files)

    change_index(n1 - 1, n2 - 1)
    sort_files()
    show_tracks()
  
  elif ans == "2":
    rename_files()
    quit()
  
  else:
    quit()

def rename_files():
  for file in files:
    audio = FLAC(file)
    title = re.sub(r'[^\w ]', "", audio["title"][0]).lower()
    title = title.replace(" ", "_")
    tracknum = audio["tracknumber"][0]
    new_name = f"{tracknum}_{title}.flac"
    p = Path(file)
    p.rename(Path(p.parent, new_name))

def show_tracks():
  print("")
  for i, file in enumerate(files):
    audio = FLAC(file)
    title = audio["title"][0]
    index = i + 1
    print(f"Track: {index} | Title: {title}")

def fill_tracknumbers():
  for file in files:
    audio = FLAC(file)
    title = audio["title"][0]
    if "tracknumber" not in audio:
      audio["tracknumber"] = "1"
      update_track(audio)

def initial_sort():
  global files
  files = sorted(files, key=lambda x: int(FLAC(x)["tracknumber"][0]))

def sort_files():
  for i, file in enumerate(files):
    audio = FLAC(file)
    tracknum = audio["tracknumber"][0]
    n = str(i + 1)
    if tracknum != n:
      audio["tracknumber"] = n
      update_track(audio)

def update_track(audio):
  title = audio["title"][0]
  print(f"Updating track: {title}")
  audio.save()

def change_index(old_index, new_index):
  files.insert(new_index, files.pop(old_index))

files = glob.glob(f"{sys.argv[1]}/*.flac")

fill_tracknumbers()
initial_sort()

while True:
  show_tracks()
  show_menu()