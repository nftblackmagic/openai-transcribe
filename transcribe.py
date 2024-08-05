from pydub import AudioSegment
from openai import OpenAI
import os

def format_time(milliseconds):
    """Convert milliseconds to SRT time format."""
    seconds, milliseconds = divmod(milliseconds, 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"

def parse_time(time_str):
    """Parse SRT time format to milliseconds."""
    h, m, s = time_str.split(':')
    s, ms = s.split(',')
    return int(h) * 3600000 + int(m) * 60000 + int(s) * 1000 + int(ms)

def adjust_srt(srt_content, offset_ms, start_index):
    """Adjust timestamps and index numbers in SRT content."""
    entries = srt_content.strip().split('\n\n')
    adjusted_entries = []
    current_index = start_index

    for entry in entries:
        lines = entry.split('\n')
        if len(lines) >= 3:  # Ensure the entry has at least 3 lines (index, timestamp, text)
            # Adjust index
            lines[0] = str(current_index)
            
            # Adjust timestamp
            time_range = lines[1].split(' --> ')
            new_start = format_time(parse_time(time_range[0]) + offset_ms)
            new_end = format_time(parse_time(time_range[1]) + offset_ms)
            lines[1] = f"{new_start} --> {new_end}"
            
            adjusted_entries.append('\n'.join(lines))
            current_index += 1

    return '\n\n'.join(adjusted_entries), current_index

# Load the audio file
song = AudioSegment.from_mp3("sam2.mp3")

# Duration of each segment in milliseconds
segment_duration = 1 * 60 * 1000

# Calculate the number of segments
num_segments = len(song) // segment_duration + (1 if len(song) % segment_duration > 0 else 0)

# Create OpenAI client
client = OpenAI()

transcriptions = []
current_index = 1

# Split and transcribe each segment
for i in range(num_segments):
    start_time = i * segment_duration
    end_time = min(start_time + segment_duration, len(song))
    segment = song[start_time:end_time]
    
    # Export the segment as a temporary file
    segment_file_name = f"segment_{i}.mp3"
    segment.export(segment_file_name, format="mp3")
    
    # Open the segment file
    with open(segment_file_name, "rb") as audio_file:
        # Transcribe the audio segment
        transcription = client.audio.transcriptions.create(
            model="whisper-1", 
            file=audio_file,
            response_format="srt"
        )
        
        # Adjust timestamps and index numbers, and add to transcriptions
        adjusted_transcription, current_index = adjust_srt(transcription, start_time, current_index)
        print(adjusted_transcription)
        transcriptions.append(adjusted_transcription)
    
    # Remove temporary segment file
    os.remove(segment_file_name)

# Combine all SRT entries into a single file
full_srt = "\n\n".join(transcriptions)

# Save the full SRT content
with open("full_transcript.srt", "w") as file:
    file.write(full_srt)

print("Full SRT transcript saved to 'full_transcript.srt'")