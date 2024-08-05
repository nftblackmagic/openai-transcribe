from pydub import AudioSegment
from openai import OpenAI  # Replace with the correct import for your OpenAI client

# Load the audio file
song = AudioSegment.from_file("flux.m4a")

# Duration of each segment in milliseconds
segment_duration = 10 * 60 * 1000

# Calculate the number of segments
num_segments = len(song) // segment_duration + (1 if len(song) % segment_duration > 0 else 0)

# Create OpenAI client
client = OpenAI()

transcriptions = []

# Split and transcribe each segment
for i in range(num_segments):
    start_time = i * segment_duration
    end_time = start_time + segment_duration
    segment = song[start_time:end_time]
    
    # Export the segment as a temporary file
    segment_file_name = f"segment_{i}.mp3"
    segment.export(segment_file_name, format="mp3")
    
    # Open the segment file
    with open(segment_file_name, "rb") as audio_file:
        # Transcribe the audio segment
        transcription = client.audio.transcriptions.create(
            model="whisper-1", 
            file=audio_file
        )
        transcriptions.append(transcription.text)
        print(transcription)
        
        

# # Combine all transcriptions into a single text
full_transcription = "".join(transcriptions)

print(full_transcription)

with open("full_transcription.txt", "w") as file:
    file.write(full_transcription)

print("Full transcription saved to 'full_transcription.txt'")

