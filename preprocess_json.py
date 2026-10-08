import requests
import os 
import json 
import pandas as pd 
import joblib



def  create_embeddings(text_list,batch_size=300):
    embedding=[]
    for item in range(0,len(text_list),batch_size):
        text_length=text_list[item:item+batch_size]
        print(f"creating embeddigns for "
              f"{item+1} to {item+batch_size}"
              f"out of  {len(text_list)}")
        r=requests.post("http://localhost:11434/api/embed",json=
                            {
                                "model":"bge-m3",
                                "input":text_length                          
                            }) 
        embedding.extend(r.json()['embeddings'])
    return embedding




my_dicts=[]
chunk_id=0

jsons=os.listdir("jsons")
for json_file in jsons:
    with open(f"jsons/{json_file}","r") as f:
        content=json.load(f)
    print(f"creating embedding for {json_file}")
    text=[c["text"] for c in content["chunk"]]
    embeddings_all=create_embeddings(text,batch_size=300)
            
    for i , chunk in enumerate(content["chunk"]):
        chunk["chunk_id"]=chunk_id
        chunk["embedding"]=embeddings_all[i]
        chunk_id+=1
        my_dicts.append(chunk)
    break
    
df=pd.DataFrame.from_records(my_dicts)
joblib.dump(df,'embed.joblib')
