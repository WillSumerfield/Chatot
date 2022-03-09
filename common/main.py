"""This file is used to generate pokedex entries given user input."""

from transformers import pipeline, AutoModelForCausalLM
from transformers import AutoTokenizer
import re
from PIL import Image, ImageTk
import threading
import tkinter as tk
from tkinter import ttk
import time
import warnings
warnings.filterwarnings("ignore")


# region Constants

WINDOW_SIZE = 768

FONT_TITLE = ('Impact', 48)

FONT_TEXT_FIELD = ('Arial', 12)

STARTUP_TIME = 2

TYPES = [
    'normal',
    'fire',
    'water',
    'grass',
    'electric',
    'ice',
    'fighting',
    'poison',
    'ground',
    'flying',
    'psychic',
    'bug',
    'rock',
    'ghost',
    'dark',
    'dragon',
    'steel',
    'fairy'
]

# endregion Constants

# region Functionality


def close_window():
    global window_closed
    window_closed = True


def import_model():
    global model
    model = AutoModelForCausalLM.from_pretrained("model")


def import_tokenizer():
    global tokenizer
    tokenizer = AutoTokenizer.from_pretrained("distilgpt2")


def center_window():
    global window
    window.update_idletasks()
    width = window.winfo_width()
    frm_width = window.winfo_rootx() - window.winfo_x()
    win_width = width + 2 * frm_width
    height = window.winfo_height()
    titlebar_height = window.winfo_rooty() - window.winfo_y()
    win_height = height + titlebar_height + frm_width
    x = window.winfo_screenwidth() // 2 - win_width // 2
    y = window.winfo_screenheight() // 2 - win_height // 2
    window.geometry('{}x{}+{}+{}'.format(width, height, x, y))
    window.deiconify()


def prompt_user():
    print("This is Chatot, a Pokedex Entry Generator. This tool is intended to inspire custom pokemon creation.")
    print("To generate pokedex entries, please enter a class and a type (ex: mouse, electric):")
    pokemon_class = input("Pokemon Classification: ")
    pokemon_type =  input("Pokemon Type:           ")

    return pokemon_class, pokemon_type


def generate_entries():

    global class_field, type_list, entry_texts

    # Get the class and type
    class_text = class_field.get()
    type_text = type_list.get()

    # Format the text
    prompt = f"< type={type_text} {class_text} > *"

    # Generate the 10 entries
    for i in range(10):

        # Generate entries until a valid one is created
        while True:

            # Generate the entry
            entry = generator(prompt, max_length=30, num_return_sequences=1, pad_token_id=50256)[0]['generated_text']

            # Remove the leading input
            entry = entry[entry.index('*') + 2:]

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
            if True: #index != -1:

                # Set the corresponding entry field
                entry_texts[i].set(entry)

                # Find the next entry
                break


# endregion Functionality

# region Initialization

# region Window Creation

# Create the window
window = tk.Tk()

# Name the window
window.title("Chatot")

# Set the icon
window.iconphoto(False, tk.PhotoImage(file='assets/chatot.png'))

# Set the taskbar icon
window.iconbitmap(default='assets/chatot.png')

# Stop the window from being resized
window.resizable(False, False)

# Set the window size
window.geometry(f"{WINDOW_SIZE}x{WINDOW_SIZE}")

# Store whether the window has been closed
window_closed = False
window.protocol("WM_DELETE_WINDOW", close_window)

# Set the window grid
window.grid_rowconfigure(0, weight=1)
window.grid_columnconfigure(0, weight=1)

# endregion Window Creation

# Import the model
model = None
model_thread = threading.Thread(target=import_model)
model_thread.start()

# Import the tokenizer
tokenizer = None
tokenizer_thread = threading.Thread(target=import_tokenizer)
tokenizer_thread.start()

# endregion Initialization

# region Run Generator

# region Run Startup

# Create a frame for the startup page
startup_frame = tk.Frame(window)
startup_frame.grid(row=0, column=0)
startup_frame.grid_rowconfigure(0, weight=1)
startup_frame.grid_columnconfigure(0, weight=1)

# Resize the Image
title_image = Image.open('assets/chatot.png')
image_size = (int(title_image.size[0]/2), int(title_image.size[1]/2))
title_image = title_image.resize((image_size[0], image_size[1]), Image.ANTIALIAS)

# Set the background image
title_image = ImageTk.PhotoImage(title_image)
title_image_label = tk.Label(startup_frame, image=title_image)
title_image_label.grid(row=0, column=0)

# Draw the title
title_text = tk.Label(startup_frame, text='CHATOT', font=FONT_TITLE)
title_text.grid(row=1, column=0, sticky=tk.N)

# Center the window
center_window()

# Run the window
start_time = time.time()
while (time.time() - start_time < STARTUP_TIME) or model_thread.is_alive() or tokenizer_thread.is_alive():
    startup_frame.update_idletasks()
    startup_frame.update()

# Clear the window
startup_frame.destroy()

# Create the text generator
generator = pipeline('text-generation', tokenizer=tokenizer, model=model)

# endregion Run Startup

# region Run Main

# Create a frame for the startup page
main_frame = tk.Frame(window)
main_frame.grid(row=0, column=0, sticky=tk.NW)
main_frame.grid_rowconfigure(0, weight=1)
main_frame.grid_columnconfigure(0, weight=1)

# Create a text field for the class
class_label = ttk.Label(main_frame, text='Class')
class_label.grid(row=0, column=0, pady=5, padx=5, sticky=tk.NW)
class_field = ttk.Entry(main_frame)
class_field.grid(row=0, column=1, pady=5, padx=5, sticky=tk.NW)

# Create a dropdown menu for types
type_label = ttk.Label(main_frame, text='Type')
type_label.grid(row=1, column=0, pady=5, padx=5, sticky=tk.NW)
type_list = tk.StringVar(main_frame)
type_list.set(TYPES[0])
type_dropdown = ttk.OptionMenu(main_frame, type_list, *TYPES)
type_dropdown.grid(row=1, column=1, pady=5, padx=5, sticky=tk.NW)

# Create a button to generate entries
generate_button = ttk.Button(main_frame, text='Generate Entries', command=generate_entries)
generate_button.grid(row=2, column=0, columnspan=2, pady=5, padx=5)

# Create a list of entries
entry_fields = [None] * 10
entry_texts = [None] * 10
for i in range(10):
    entry_texts[i] = tk.StringVar()
    entry_fields[i] = ttk.Label(main_frame, textvariable=entry_texts[i], anchor=tk.E, wraplength=WINDOW_SIZE * 3/4)
    entry_fields[i].grid(row=i, column=2, pady=5, padx=5, sticky=tk.W)

# Run the window
while not window_closed:
    main_frame.update_idletasks()
    main_frame.update()

# endregion Run Main

# endregion Run Generator
