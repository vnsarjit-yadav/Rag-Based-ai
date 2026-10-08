import os 
import subprocess

file=os.listdir("videos")

for item in range(len(file)):
    subprocess.run(["ffmpeg","-i",f"videos/{file[item]}",f"audios/video-audio{item+1}.mp3"])
    print("successfully...")
    
   


