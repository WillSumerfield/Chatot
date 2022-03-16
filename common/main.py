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

DESCRIPTION = """This is Chatot, a Pokedex Entry Generator. 
The aim of this application is to generate pokedex entries for new pokemon, based on a class and type that you provide. 
To generate novel Pokedex entries, you need to input a class and a type. 
The class is the object that the pokemon is based on, such as 'mouse', 'keychain', or 'tree', written in  all lowercase.
You can input multiple classes separated by spaces, although the fewer classes you add, the more your results are likely to be focused on those classes. 
Click the 'Generate Entries' button to generate 10 new novel pokedex entries. You can highlight and copy any entries you like.""".replace('\n', ' ')

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


def start_generating_entries():

    # Create a thread for generating entries
    entry_generation_thread = threading.Thread(target=generate_entries, args=(class_field.get(), type_list.get()))

    # Run the thread
    entry_generation_thread.start()


def generate_entries(class_text, type_text):

    global entry_list

    # Format the text
    prompt = f"< type={type_text} {class_text} > * "

    # Generate the 10 entries
    for i in range(10):

        # Generate entries until a valid one is created
        while True:

            # Generate the entry
            entry = generator(prompt, max_length=60, num_return_sequences=1, pad_token_id=50256)[0]['generated_text']

            # Remove the leading input
            entry = entry[entry.index('*') + 2:]

            # Strip whitespace
            entry = entry.strip()

            # Find the index of each period in the entry
            periods = [per.start() for per in re.finditer(r'\.', entry)]
            periods.sort()

            # Find the first period past the 30 character place
            index = -1
            for period in periods:
                if period > 40:
                    index = period
                    break

            # If no valid periods were found, generate a new entry
            if index != -1:

                # Cut off the entry at the last period
                index = periods[-1]
                entry = entry[:index + 1]

                # Capitalize the beginning of every sentence
                result = ''
                sentences = entry.split('. ')
                for s in sentences:
                    s = s.capitalize()
                    result = result + s + '. '
                result = result.strip()
                result = result[:-1]

                # Store the entry in the entry list, and generate the next entry
                entry_list[i] = result
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
# window.iconbitmap(default='assets/chatot.png')

# Stop the window from being resized
window.resizable(False, False)

# Set the window size
window.geometry(f"{WINDOW_SIZE}x{WINDOW_SIZE}")

# Store whether the window has been closed
window_closed = False
window.protocol("WM_DELETE_WINDOW", close_window)

# endregion Window Creation

# A list of the displayed generated pokedex entries
entry_list = [""] * 10

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
startup_canvas = tk.Canvas(window)
startup_canvas.pack()

# Resize the Image
title_image = Image.open('assets/chatot.png')
image_size = (int(title_image.size[0]/2), int(title_image.size[1]/2))
title_image = title_image.resize((image_size[0], image_size[1]), Image.ANTIALIAS)

# Set the background image
title_image = ImageTk.PhotoImage(title_image)
title_image_label = tk.Label(window, image=title_image)
title_image_label.place(x=WINDOW_SIZE/2, y=WINDOW_SIZE * (2/5), anchor=tk.CENTER)

# Draw the title
title_text = tk.Label(window, text='CHATOT', font=FONT_TITLE)
title_text.place(x=WINDOW_SIZE/2, y=WINDOW_SIZE * (3/4), anchor=tk.CENTER)

# Center the window
center_window()

# Run the window
start_time = time.time()
while (time.time() - start_time < STARTUP_TIME) or model_thread.is_alive() or tokenizer_thread.is_alive():
    startup_canvas.update_idletasks()
    startup_canvas.update()

# Create the text generator
generator = pipeline('text-generation', tokenizer=tokenizer, model=model)

# endregion Run Startup

# region Run Main

# Create a frame for the startup page
main_canvas = tk.Canvas(window, width=WINDOW_SIZE, height=WINDOW_SIZE, highlightthickness=0)
main_canvas.place(x=0, y=0)

# Create a title
title_label = ttk.Label(main_canvas, text='CHATOT', font=FONT_TITLE)
title_label.place(x=WINDOW_SIZE/2, y=WINDOW_SIZE/16, anchor=tk.CENTER)

# Create a description
description_label = ttk.Label(main_canvas, text=DESCRIPTION, anchor=tk.CENTER, wraplength=WINDOW_SIZE * 3/4)
description_label.place(x=WINDOW_SIZE/2, y=WINDOW_SIZE * (7/64), anchor=tk.N)

# Draw a line
main_canvas.create_line(0, WINDOW_SIZE/4, WINDOW_SIZE, WINDOW_SIZE/4)

# Create a text field for the class
class_label = ttk.Label(main_canvas, text='Class')
class_label.place(x=WINDOW_SIZE/4 - 4, y=WINDOW_SIZE * (5/16), anchor=tk.E)
class_field = ttk.Entry(main_canvas)
class_field.place(x=WINDOW_SIZE/4, y=WINDOW_SIZE * (5/16), anchor=tk.W)

# Create a dropdown menu for types
type_label = ttk.Label(main_canvas, text='Type')
type_label.place(x=WINDOW_SIZE * (15/24), y=WINDOW_SIZE * (5/16), anchor=tk.E)
type_list = tk.StringVar(main_canvas)
type_list.set(TYPES[0])
type_dropdown = ttk.OptionMenu(main_canvas, type_list, *TYPES)
type_dropdown.place(x=WINDOW_SIZE * (15/24), y=WINDOW_SIZE * (5/16), anchor=tk.W)

# Create a button to generate entries
generate_button = ttk.Button(main_canvas, text='Generate Entries', command=start_generating_entries)
generate_button.place(x=WINDOW_SIZE/2, y=WINDOW_SIZE * (3/8), anchor=tk.CENTER)

# Create a list of entries
entry_fields = [None] * 10
for i in range(10):
    entry_fields[i] = tk.Text(main_canvas, width=35, height=4, bd=0, bg=window.cget('bg'), wrap=tk.WORD)
    entry_fields[i].configure(state='disabled')
    entry_fields[i].place(y=WINDOW_SIZE * (15/32) + (80 * (i % 5)), x=WINDOW_SIZE * (1 + (8 * (i // 5)))/16, anchor=tk.NW)

# Run the window
while not window_closed:

    # Update the window
    main_canvas.update_idletasks()
    main_canvas.update()

    # Update each entry
    for i in range(len(entry_list)):

        # Check if the entry has already been set
        if entry_list[i] is not None:

            # Update the entry
            entry_fields[i].configure(state='normal')
            entry_fields[i].delete(1.0, 'end')
            entry_fields[i].insert(1.0, entry_list[i])
            entry_fields[i].configure(state='disabled')

            entry_list[i] = None

# endregion Run Main

# endregion Run Generator
