"""This file is used to generate pokedex entries given user input."""

from transformers import pipeline, AutoModelForCausalLM
from transformers import AutoTokenizer
import re
import threading
import tkinter as tk
from PIL import Image
import warnings
warnings.filterwarnings("ignore")

# region Functionality


def import_model():
    global model
    model = AutoModelForCausalLM.from_pretrained("model")


def startup_display():

    # Print the startup image
    ("assets/chatot.jpg")

    # Run until the model is done importing
    global model_thread
    while model_thread.is_alive():
        pass



def prompt_user():
    print("This is Chatot, a Pokedex Entry Generator. This tool is intended to inspire custom pokemon creation.")
    print("To generate pokedex entries, please enter a class and a type (ex: mouse, electric):")
    pokemon_class = input("Pokemon Classification: ")
    pokemon_type =  input("Pokemon Type:           ")

    return pokemon_class, pokemon_type


def generate_entries(pokemon_class, pokemon_type):

    # Format the text
    prompt = f"< type={pokemon_type} {pokemon_class} > *"

    # Create a list of entries
    entries = [''] * 10

    # Generate the 10 entries
    for i in range(10):

        # Generate entries until a valid one is created
        while True:

            # Generate the entry
            entry = generator(prompt, max_length=30, num_return_sequences=1, pad_token_id=50256)[0]['generated_text']

            # Remove the leading input
            entry = entry[entry.index('*') + 1:]

            # Replace the PERIOD token with a period
            entry = re.sub(" PERIOD", ".", entry)

            # Find the index of each period in the entry
            periods = [per.start() for per in re.finditer(r'\.', entry)]

            # Find the first period after the cutoff
            index = -1
            for per in periods:

                # Use the first period past the cutoff
                if per > 30:
                    index = per
                    break

            # If no periods were used, generate a new entry and try again
            if index != -1:
                entries[i] = entry[:index]
                break

    return entries


# endregion Functionality

# region Initialization

# Create the window
window = tk.Tk()

# Import the model
model_thread = threading.Thread(target=import_model)
model_thread.start()

# Show the startup display
startup_display()

# Create the tokenizer instance
tokenizer = AutoTokenizer.from_pretrained("distilgpt2")

# Create the text generator
generator = pipeline('text-generation', tokenizer=tokenizer, device=0, model=model)

# endregion Initialization

# region Run Generator


# Rerun the Program indefinitely until the user stops it
while True:

    # Clear the console
    print("\033[H\033[J", end="")

    # Prompt the user
    pokemon_class, pokemon_type = prompt_user()

    # Generate entries based on the prompt
    entries = generate_entries(pokemon_class, pokemon_type)

    # Output Each Entry
    for i in range(len(entries)): print(f"Entry {i}: {entries[i]}")

# endregion Run Generator
