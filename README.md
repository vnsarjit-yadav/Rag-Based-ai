# How to use this RAG AI Teaching Assistant on your own data

This project is a RAG-based AI Teaching Assistant that allows users to
ask questions related to their course videos and find the relevant
video, topic, and timestamp.

The complete workflow is:

Videos → MP3 → JSON → Embeddings → Relevant Context → LLM → Answer

------------------------------------------------------------------------

## Requirements

Before using this project, make sure the following are installed:

-   Python
-   FFmpeg
-   Ollama
-   Whisper
-   BGE-M3
-   Llama 3.2

Python libraries required:

``` bash
pip install openai-whisper
pip install pandas
pip install numpy
pip install scikit-learn
pip install joblib
pip install requests
```

------------------------------------------------------------------------

## Ollama Setup

This project uses Ollama to run the embedding model and LLM locally.

Install the required models.

For generating embeddings:

``` bash
ollama pull bge-m3
```

For generating the final answer:

``` bash
ollama pull llama3.2
```

You can check the installed models using:

``` bash
ollama list
```

Make sure Ollama is running before executing `preprocess_json.py` and
`process_incoming.py`.

------------------------------------------------------------------------

## Project folder structure

The project should have the following structure:

``` text
Rag-Based-ai/
│
├── audios/
├── jsons/
├── unused/
├── videos/
│
├── embeddings.joblib
├── mp3_to_json.py
├── preprocess_json.py
├── process_incoming.py
├── prompt.txt
├── responce.txt
├── video_to_mp3.py
└── README.md
```

The `videos` folder contains the original course videos.

The `audios` folder contains the MP3 files generated from the videos.

The `jsons` folder contains the transcribed JSON files generated from
the MP3 files.

The `embeddings.joblib` file contains the processed course data and
embeddings.

`prompt.txt` and `responce.txt` are supporting/output files used during
the question-answering process.

------------------------------------------------------------------------

## Step 1 - Collect your videos

Move all your video files to the `videos` folder.

For example:

``` text
videos/
├── video-0.mp4
├── video-1.mp4
├── video-2.mp4
└── ...
```

You don't need to manually add anything to the `audios` or `jsons`
folders.

These folders will be populated by the Python scripts in the next steps.

------------------------------------------------------------------------

## Step 2 - Convert to mp3

Convert all the video files to MP3 by running:

``` bash
python video_to_mp3.py
```

This script uses **FFmpeg** to extract the audio from the videos.

The flow is:

``` text
videos/
    ↓
video_to_mp3.py
    ↓
audios/
```

For example:

``` text
video-0.mp4
       ↓
video-0.mp3

video-1.mp4
       ↓
video-1.mp3
```

The generated MP3 files will be stored inside the `audios` folder.

### Why do we convert videos to MP3?

The next step uses Whisper to understand the spoken content of the
course. Therefore, the audio needs to be extracted from the videos
first.

------------------------------------------------------------------------

## Step 3 - Convert mp3 to json

Convert all the MP3 files to JSON by running:

``` bash
python mp3_to_json.py
```

This script uses **Whisper** to transcribe the audio into text.

The flow is:

``` text
audios/
    ↓
mp3_to_json.py
    ↓
Whisper
    ↓
jsons/
```

The generated JSON files contain the video information, timestamps, and
transcribed text.

A typical chunk looks like:

``` json
{
    "number": "2",
    "title": "video-audio2",
    "start": 125.4,
    "end": 138.7,
    "text": "Today we will learn binary search trees."
}
```

Each chunk contains:

-   `number` → Video number
-   `title` → Video title
-   `start` → Starting timestamp in seconds
-   `end` → Ending timestamp in seconds
-   `text` → Transcribed text

### Why are timestamps important?

Timestamps allow the system to tell the student exactly where a
particular topic is taught.

For example:

``` text
Video 5
08:35 - 10:20
Binary Search Tree insertion
```

So instead of searching through the entire video, the student can
directly go to the relevant timestamp.

------------------------------------------------------------------------

## Step 4 - Convert the json file to Vectors

Use the file `preprocess_json.py` to convert the JSON files into a
dataframe containing the course information and embeddings, and save it
as a joblib file.

Run:

``` bash
python preprocess_json.py
```

The flow is:

``` text
jsons/
    ↓
preprocess_json.py
    ↓
BGE-M3
    ↓
Embeddings
    ↓
embeddings.joblib
```

The script extracts the text from the JSON chunks and sends the text to
the **BGE-M3 embedding model**.

BGE-M3 converts the text into numerical vectors.

For example:

``` text
"Binary Search Tree insertion"
              ↓
           BGE-M3
              ↓
[0.12, -0.34, 0.56, ...]
```

These vectors represent the semantic meaning of the text.

The dataframe contains information such as:

``` text
chunk_id
number
title
start
end
text
embedding
```

The final processed data is stored in:

``` text
embeddings.joblib
```

### Why do we convert text into vectors?

Vectors allow the system to perform semantic search.

For example, the user may ask:

``` text
How do I add a new node to a BST?
```

But the video transcript may contain:

``` text
Today we will learn how to insert elements into a Binary Search Tree.
```

Even though the exact words are different, the meaning is similar.

The embeddings help the system understand this similarity.

------------------------------------------------------------------------

## Step 5 - Prompt generation and feeding to LLM

Read the joblib file through `process_incoming.py` and load it into
memory.

Run:

``` bash
python process_incoming.py
```

The user can then enter a question related to the course.

For example:

``` text
Ask a Question..

Where is Binary Search Tree deletion taught?
```

The question is first converted into an embedding using BGE-M3.

The system then compares the question embedding with the embeddings
stored in `embeddings.joblib`.

This is done using **Cosine Similarity**.

The flow is:

``` text
User Question
      ↓
BGE-M3
      ↓
Question Embedding
      ↓
Cosine Similarity
      ↓
Most Relevant Course Chunks
```

The most relevant chunks are selected and added to a prompt.

The prompt contains information such as:

-   Video title
-   Video number
-   Starting timestamp
-   Ending timestamp
-   Transcribed text

The generated prompt is then fed to the **Llama 3.2** language model.

The final flow is:

``` text
User Question
      ↓
Question Embedding
      ↓
Semantic Search
      ↓
Relevant Video Chunks
      ↓
Prompt Generation
      ↓
Llama 3.2
      ↓
Final Answer
```

For example, the system may generate an answer like:

``` text
Binary Search Tree deletion is covered in Video 12.

The relevant section starts around 08:35 and
continues until approximately 12:40.

You can go to Video 12 and start watching
from around 08:35.
```

This allows students to quickly find the exact location where their
topic is taught.

------------------------------------------------------------------------

## Complete workflow

The complete project works in the following order:

``` text
                    Course Videos
                         │
                         ▼
               video_to_mp3.py
                         │
                         ▼
                      MP3 Audio
                         │
                         ▼
                 mp3_to_json.py
                         │
                         ▼
                  JSON + Timestamps
                         │
                         ▼
               preprocess_json.py
                         │
                         ▼
                  BGE-M3 Embeddings
                         │
                         ▼
                 embeddings.joblib
                         │
                         ▼
               process_incoming.py
                         │
                         ▼
                    User Question
                         │
                         ▼
                  Question Embedding
                         │
                         ▼
                  Cosine Similarity
                         │
                         ▼
                Relevant Course Chunks
                         │
                         ▼
                   Prompt Generation
                         │
                         ▼
                     Llama 3.2
                         │
                         ▼
                    Final Answer
```

------------------------------------------------------------------------

## Order in which you should run the files

Always run the files in this order:

### 1. `video_to_mp3.py`

``` bash
python video_to_mp3.py
```

### 2. `mp3_to_json.py`

``` bash
python mp3_to_json.py
```

### 3. `preprocess_json.py`

``` bash
python preprocess_json.py
```

### 4. `process_incoming.py`

``` bash
python process_incoming.py
```

The output of one step is used as the input for the next step.

``` text
videos
   ↓
audios
   ↓
jsons
   ↓
embeddings.joblib
   ↓
process_incoming.py
   ↓
Answer
```

**Important:** `prompt.txt` and `responce.txt` do not need to be run
manually. They are supporting/output files used during the
question-answering process.

------------------------------------------------------------------------

## How the RAG system works

RAG stands for **Retrieval-Augmented Generation**.

Instead of directly asking the LLM to answer the question, the system
first retrieves the most relevant information from the user's course.

The process is:

``` text
User Question
      ↓
Retrieve relevant course content
      ↓
Add retrieved content to prompt
      ↓
Send context + question to LLM
      ↓
Generate final answer
```

This allows the AI to answer questions specifically using the content
available in the course.

------------------------------------------------------------------------

## Why use BGE-M3?

BGE-M3 is used to convert both the course content and the user's
question into embeddings.

This allows the system to perform semantic search instead of simple
keyword matching.

For example:

``` text
User:
How can I insert a node into a BST?

Course:
We will now learn how to add an element
to a Binary Search Tree.
```

The wording is different, but the meaning is similar.

BGE-M3 helps the system identify this relationship.

------------------------------------------------------------------------

## Why use Cosine Similarity?

Cosine similarity is used to compare the question embedding with the
embeddings of all course chunks.

Conceptually:

``` text
Question Embedding
        ↓
Compare with all course embeddings
        ↓
Similarity Scores
        ↓
Highest Scores
        ↓
Most Relevant Chunks
```

The most relevant chunks are then provided to the LLM.

------------------------------------------------------------------------

## Why use Llama 3.2?

Llama 3.2 is used to generate the final human-readable answer.

The retrieved course chunks are provided to the model along with
instructions about how the answer should be generated.

The LLM can then explain:

-   Which video contains the topic
-   Which timestamp is relevant
-   What is taught there
-   Where the student should start watching

------------------------------------------------------------------------

## Example

Suppose your course contains hundreds of videos.

The user asks:

``` text
Where is recursion explained?
```

The system performs:

``` text
Question
   ↓
BGE-M3 Embedding
   ↓
Cosine Similarity
   ↓
Top Relevant Chunks
   ↓
Prompt
   ↓
Llama 3.2
```

The system may return:

``` text
Recursion is explained in Video 8.

The relevant content starts around 12:30
and continues until approximately 15:10.

Go to Video 8 and start from around 12:30.
```

The student does not need to manually search through all the videos.

------------------------------------------------------------------------

## Adding new videos

If you add new videos to the `videos` folder, you need to process them
through the complete pipeline again.

Run:

``` bash
python video_to_mp3.py
```

then:

``` bash
python mp3_to_json.py
```

then:

``` bash
python preprocess_json.py
```

After the embeddings have been generated, you can ask questions using:

``` bash
python process_incoming.py
```

If the course content has not changed and `embeddings.joblib` already
exists, you only need to run:

``` bash
python process_incoming.py
```

to ask new questions.

------------------------------------------------------------------------

## Technologies used

  Technology     Purpose
  -------------- -------------------------------
  Python         Main programming language
  FFmpeg         Video to MP3 conversion
  Whisper        Audio transcription
  BGE-M3         Text embeddings
  Ollama         Running AI models locally
  Llama 3.2      Final answer generation
  Pandas         Data processing
  NumPy          Numerical operations
  Scikit-learn   Cosine similarity
  Joblib         Saving and loading embeddings
  JSON           Storing transcript data

------------------------------------------------------------------------

## Common errors

### Ollama connection error

If you get a connection error while generating embeddings or answers,
make sure Ollama is running.

Check:

``` bash
ollama list
```

------------------------------------------------------------------------

### Model not found

If BGE-M3 is not available:

``` bash
ollama pull bge-m3
```

If Llama 3.2 is not available:

``` bash
ollama pull llama3.2
```

------------------------------------------------------------------------

### FFmpeg not found

If you get:

``` text
'ffmpeg' is not recognized as an internal or external command
```

install FFmpeg and add it to your system PATH.

After adding FFmpeg to PATH, restart VS Code.

------------------------------------------------------------------------

### embeddings.joblib not found

Make sure you have successfully run:

``` bash
python preprocess_json.py
```

before running:

``` bash
python process_incoming.py
```

The `embeddings.joblib` file is created during the preprocessing step.

------------------------------------------------------------------------

## Important points

-   Always follow the execution order.
-   Keep your course videos inside the `videos` folder.
-   Do not manually modify the generated JSON files unless you know what
    you are changing.
-   Make sure Ollama is running before generating embeddings or asking
    questions.
-   Make sure both `bge-m3` and `llama3.2` are installed in Ollama.
-   If you add new course videos, process the videos again before asking
    questions about the new content.

------------------------------------------------------------------------

## Future improvements

This project can be extended into a complete AI Learning Assistant.

Some possible improvements are:

-   Web-based user interface
-   Direct video playback
-   Clickable timestamps
-   Multiple course support
-   Better semantic search
-   Vector database integration
-   Automatic notes generation
-   Automatic quiz generation
-   Student progress tracking
-   Conversational chat history
-   Re-ranking of retrieved results

For example, instead of only showing:

``` text
Video 12 - 08:35
```

a future version could provide a:

``` text
▶ Watch from 08:35
```

button that directly opens the video at the relevant timestamp.

------------------------------------------------------------------------

## Final project flow

The complete RAG AI Teaching Assistant can be understood in one simple
flow:

``` text
Videos
   ↓
Convert to MP3
   ↓
Transcribe using Whisper
   ↓
Create JSON with timestamps
   ↓
Create BGE-M3 embeddings
   ↓
Save embeddings.joblib
   ↓
User asks a question
   ↓
Convert question to embedding
   ↓
Find relevant chunks using Cosine Similarity
   ↓
Create prompt using retrieved chunks
   ↓
Send prompt to Llama 3.2
   ↓
Generate final answer
```

The main purpose of this project is to make long educational video
courses **searchable using natural language**, so that students can ask
a question and quickly find **where that topic is taught in the
course**.
