import pandas as pd 
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import joblib
import requests

def  create_embeddings(text_list):
    r=requests.post("http://localhost:11434/api/embed",json=
                        {
                            "model":"bge-m3",
                            "input":text_list
                        }) 
    embedding=r.json()['embeddings']
    return embedding

def inference(prompt):
     r=requests.post("http://localhost:11434/api/generate",json=
                            {
                                "model":"llama3.2",
                                "prompt":prompt,
                                "stream":False                   
                            })
     response=r.json()
     return response

df=joblib.load('embeddings.joblib')


incoming_query=input("Ask a Question..")
question_embedding=create_embeddings([incoming_query])[0]


similarties=cosine_similarity(np.vstack(df['embedding']),[question_embedding]).flatten() 
top_results=5
max_indx=similarties.argsort()[::-1][0:top_results]

new_df=df.loc[max_indx]

prompt=f'''
I am teaching  DSA using C++ in this course. Hare are video subtitle chunks containing 
video title, video number ,start time in second ,end time in second ,the text at that time:

"{new_df[["title","number","start","end","text"]].to_json(orient="records")}" 
------------------------------------------------------------------------------
"{incoming_query}"
user asked this question related to the video chunks,you have to answer where and how much 
content is taught in which video (in which video and at what timestamp) and guide the user to go 
in that perticular video.If user asks unrelated question. tell him that you can only answer 
question related to this course.
'''
with  open("prompt.txt","w") as f:
    f.write(prompt)

response=inference(prompt)['response']
with  open("response.txt","w") as f:
    f.write(response)
print(inference(response))

    