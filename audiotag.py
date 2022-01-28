import sys
import glob
import re
import mutagen
from pathlib import Path

def show_menu():
  print("")
  print("title - Change a track's title")
  print("artist - Change a track's artist")
  print("artistall - Change the album's artist")
  print("move - Move track to a new position")
  print("rename - Apply filename changes")

  ans = input("> ")

  if ans == "title":
    n = int(input("Track Number: "))
    t = input("New Track Title: ")
    if n <= 0 or n > len(files):
      return
    changeone(n - 1, "title", t)  

  elif ans == "artist":
    n = int(input("Track Number: "))
    a = input("New Track Artist: ")
    if n <= 0 or n > len(files):
      return
    changeone(n - 1, "artist", a)

  elif ans == "artistall":
    a = input("New Artist Name: ")
    changeall("artist", a)   

  elif ans == "move":
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
    show_tracks()
  
  elif ans == "rename":
    rename_files()
    quit()
  
  else:
    quit()

def rename_files():
  for file in files:
    audio = mutagen.File(file)
    title = re.sub(r'[^\w ]', "", audio["title"][0]).lower()
    title = title.replace(" ", "_")
    tracknum = audio["tracknumber"][0]
    new_name = f"{tracknum}_{title}.flac"
    p = Path(file)
    p.rename(Path(p.parent, new_name))

def show_tracks():
  print("")
  for i, file in enumerate(files):
    audio = mutagen.File(file)
    title = audio["title"][0]
    artist = audio["artist"][0]
    index = i + 1
    print(f"Track: {index} | Artist: {artist} | Title: {title}")

def check_tracks():
  for file in files:
    audio = mutagen.File(file)
    title = audio["title"][0]
    if "tracknumber" not in audio:
      audio["tracknumber"] = "1"
      update_track(audio)
      changeone("tracknumber")
    if "title" not in audio or audio["title"][0].strip() == "":
      audio["title"] = Path(file).stem.strip()
      update_track(audio)
    if "artist" not in audio or audio["artist"][0].strip() == "":
      audio["artist"] = "Anon"
      update_track(audio)      

def update_tracknumbers():
  for i, file in enumerate(files):
    audio = mutagen.File(file)
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

def changeall(field, value):
  for i, file in enumerate(files):
    changeone(i, field, value)

def changeone(index, field, value):
  audio = mutagen.File(files[index])
  audio[field] = value
  update_track(audio)

def initial_sort():
  global files
  files = sorted(files, key=lambda x: int(mutagen.File(x)["tracknumber"][0]))

files = glob.glob(f"{sys.argv[1]}/*.flac")

check_tracks()
initial_sort()

while True:
  show_tracks()
  show_menu()