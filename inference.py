# Import necessary libraries
import whisper
import numpy as np
from timeit import default_timer as timer
import tflite_runtime.interpreter as tflite

# Define the path to the TFLite model
tflite_model_path = './model/whisper-base.tflite'

# Create an interpreter to run the TFLite model
interpreter = tflite.Interpreter(model_path=tflite_model_path)

# Allocate memory for the interpreter
interpreter.allocate_tensors()

# Get the input and output tensors
input_tensor = interpreter.get_input_details()[0]['index']
output_tensor = interpreter.get_output_details()[0]['index']

inference_start = timer()

# Calculate the mel spectrogram of the audio file
print(f'Calculating mel spectrogram...')
mel_from_file = whisper.audio.log_mel_spectrogram('./audio_files/jackhammer.wav')

# Pad or trim the input data to match the expected input size
input_data = whisper.audio.pad_or_trim(mel_from_file, whisper.audio.N_FRAMES)

# Add a batch dimension to the input data
input_data = np.expand_dims(input_data, 0)

# Run the TFLite model using the interpreter
print("Invoking interpreter ...")
interpreter.set_tensor(input_tensor, input_data)
interpreter.invoke()

# Get the output data from the interpreter
output_data = interpreter.get_tensor(output_tensor)

# Create a tokenizer to convert tokens to text
wtokenizer = whisper.tokenizer.get_tokenizer(True, language="ja")

# Convert tokens to text
print("Converting tokens ...")
for token in output_data:
    # Replace -100 with the end of text token
    token[token == -100] = wtokenizer.eot
    text = wtokenizer.decode(token)
    print(text)

print("\nInference took {:.2f}s ".format(timer() - inference_start))

