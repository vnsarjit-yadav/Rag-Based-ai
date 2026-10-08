import whisper
import json 
import os

model=whisper.load_model("large-v2")

audios=os.listdir("audios")
for audio in audios:
    if "-" in audio:
        number=audio.split(".")[0][-1]
        video=audio.split(".")[0]
        result=model.transcribe(
                        audio=f"audios/{audio}",
                        language="en",
                        task="translate",
                        word_timestamps=False
                        
                )
        chunks=[]
        for item in result["segments"]:
            chunks.append({"number":number,"title":video,"start":item["start"],"end":item["end"],"text":item["text"]})
        chunks_with_metadata={"chunk":chunks,"text":result["text"]}
        with open(f"jsons/{audio}.json","w") as f:
            json.dump(chunks_with_metadata,f) 
            
    print(f"{audios.index(audio)+1} file chunking completed successfully..")