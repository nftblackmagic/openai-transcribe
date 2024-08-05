from openai import OpenAI

client = OpenAI()

def estimate_token_count(text):
    return len(text) // 4

# Load the full transcription from the file
with open("full_transcription.txt", "r") as file:
    full_transcription = file.read()

# Maximum tokens per piece
max_tokens = 500
max_characters = max_tokens * 4

# Split the transcription into smaller pieces
transcription_pieces = []
start = 0

while start < len(full_transcription):
    end = start + max_characters
    
    # Ensure we don't cut off in the middle of a word
    if end < len(full_transcription):
        end = full_transcription.rfind(' ', start, end)
    
    piece = full_transcription[start:end]
    transcription_pieces.append(piece)
    
    start = end
    
combined_response = ""
# Output the pieces to verify
for i, piece in enumerate(transcription_pieces):
    # print(f"Piece {i+1} (tokens: {estimate_token_count(piece)})")
    print(piece[:1000])  # Print the first 1000 characters of each piece as a sample
    print("\n")
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful Chinese transcript revising expert. User will give you a video script. Please help user to remove only the repeated parts with minimal changes. Do not use creative language, do not add new content, and keep all the examples user provided."},
            {"role": "user", "content": piece}
        ]
        )
    
    print(response.choices[0].message.content)
    
    transcript = response.choices[0].message.content
    
    combined_response += transcript + "\n"
    
    with open(f"transcription_piece_{i+1}.txt", "w") as file:
        file.write(transcript)

with open("combined_transcription.txt", "w") as file:
    file.write(combined_response.replace(' ', '\n'))

