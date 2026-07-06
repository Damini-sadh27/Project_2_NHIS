from tkinter import *
from tkinter import filedialog, messagebox
import math
import re

# =========================================================
# OPTIONAL GRAPH SUPPORT
# Install with:
# pip install matplotlib numpy
# =========================================================
try:
    import matplotlib.pyplot as plt
    import numpy as np
    GRAPH_AVAILABLE = True
except ImportError:
    GRAPH_AVAILABLE = False


# =========================================================
# MAIN WINDOW
# =========================================================
root = Tk()
root.title("🧮 Smart Scientific Calculator")
root.geometry("760x820")
root.minsize(720, 760)



# =========================================================
# GLOBAL VARIABLES / STATE
# =========================================================
first_number = None
operator = None

memory = 0.0
history_items = []

angle_mode = "DEG"
dark_mode = True


# =========================================================
# THEMES
# =========================================================
THEMES = {
    "dark": {
        "root": "#1E1E1E",
        "panel": "#252525",
        "display_bg": "#F8F9FA",
        "display_fg": "#212529",
        "number": "#3B3B3B",
        "function": "#34495E",
        "operator": "#F39C12",
        "danger": "#E74C3C",
        "warning": "#E67E22",
        "equal": "#2ECC71",
        "text": "white",
        "history_bg": "#161616",
        "history_fg": "#F1F1F1"
    },

    "light": {
        "root": "#ECEFF1",
        "panel": "#FFFFFF",
        "display_bg": "#FFFFFF",
        "display_fg": "#202124",
        "number": "#E3E7EA",
        "function": "#607D8B",
        "operator": "#F9A825",
        "danger": "#D84343",
        "warning": "#EF6C00",
        "equal": "#2E7D32",
        "text": "#202124",
        "history_bg": "#F7F7F7",
        "history_fg": "#202124"
    }
}



# =========================================================
# HELPER FUNCTIONS
# =========================================================
def show_error():
    """
    Show Error instead of crashing.
    """
    display.delete(0, END)
    display.insert(END, "Error")


def get_number():
    """
    Get current number from display safely.
    """
    text = display.get().strip()

    if not text or text == "Error":
        raise ValueError("Invalid input")

    return float(text)


def format_result(result):
    """
    Professional result formatting.

    Example:
    25.0 -> 25
    5.500000 -> 5.5
    """

    if isinstance(result, complex):
        return str(result)

    if not math.isfinite(float(result)):
        return "Error"

    # Remove tiny floating-point errors
    if abs(result) < 1e-12:
        result = 0

    # Convert whole float to integer
    if float(result).is_integer():
        return str(int(result))

    # Limit unnecessary decimal digits
    return f"{result:.12g}"


def set_display(value):
    """
    Replace display content.
    """
    display.delete(0, END)
    display.insert(END, value)


def add_history(expression, result):
    """
    Add calculation to history.
    """

    line = f"{expression} = {format_result(result)}"

    history_items.append(line)
    history_list.insert(END, line)

    # Scroll automatically
    history_list.yview(END)


def safe_unary(symbol, function, validator=None):
    """
    Generic safe function for operations
    using only one number.

    Examples:
    sqrt
    square
    log
    percentage
    """

    try:
        number = get_number()

        if validator and not validator(number):
            raise ValueError

        result = function(number)

        set_display(format_result(result))

        add_history(
            f"{symbol}({format_result(number)})",
            result
        )

    except (
        ValueError,
        TypeError,
        OverflowError,
        ZeroDivisionError
    ):
        show_error()


# =========================================================
# NUMBER INPUT FUNCTIONS
# =========================================================
def button_click(value):
    """
    Add number to display.
    """

    current = display.get()

    if current == "Error":
        display.delete(0, END)

    display.insert(END, value)


def decimal():
    """
    Add decimal point safely.
    """

    current = display.get()

    if current == "Error":
        current = ""
        display.delete(0, END)

    if "." not in current:

        if not current:
            display.insert(END, "0.")

        else:
            display.insert(END, ".")


def clear_display():
    """
    Clear display and reset operator.
    """

    global first_number, operator

    display.delete(0, END)

    first_number = None
    operator = None


def backspace():
    """
    Remove last character.
    """

    if display.get() == "Error":
        clear_display()

    else:
        display.delete(
            max(0, len(display.get()) - 1),
            END
        )


def plus_minus():
    """
    Change positive number to negative
    and negative to positive.
    """

    try:
        number = get_number()

        set_display(
            format_result(-number)
        )

    except ValueError:
        show_error()


# =========================================================
# BASIC OPERATOR FUNCTION
# =========================================================
def get_operator(op):
    """
    Store first number and operator.

    Prevents:
    - empty operator
    - operator twice
    - invalid input
    """

    global first_number, operator

    try:

        if (
            not display.get().strip()
            or display.get() == "Error"
        ):
            raise ValueError

        first_number = get_number()

        operator = op

        display.delete(0, END)

    except ValueError:
        show_error()


# =========================================================
# CALCULATE RESULT
# =========================================================
def calculate_result():
    """
    Calculate:
    +
    -
    *
    /
    ^
    """

    global first_number, operator

    try:

        # Pressing = without valid calculation
        if first_number is None or operator is None:
            raise ValueError

        second_number = get_number()

        operations = {
            "+": lambda a, b: a + b,
            "-": lambda a, b: a - b,
            "*": lambda a, b: a * b,
            "/": lambda a, b: a / b,
            "^": lambda a, b: a ** b
        }

        # Division by zero
        if operator == "/" and second_number == 0:
            raise ZeroDivisionError

        result = operations[operator](
            first_number,
            second_number
        )

        expression = (
            f"{format_result(first_number)} "
            f"{operator} "
            f"{format_result(second_number)}"
        )

        set_display(
            format_result(result)
        )

        add_history(
            expression,
            result
        )

        # Reset calculation
        first_number = None
        operator = None

    except (
        ValueError,
        ZeroDivisionError,
        OverflowError,
        TypeError
    ):

        first_number = None
        operator = None

        show_error()


# =========================================================
# SQUARE ROOT
# =========================================================
def square_root():

    safe_unary(
        "√",
        math.sqrt,
        lambda x: x >= 0
    )


# =========================================================
# SQUARE
# =========================================================
def square():

    safe_unary(
        "square",
        lambda x: x ** 2
    )


# =========================================================
# FACTORIAL n!
# =========================================================
def factorial():
    """
    Calculate factorial.

    Example:
    5! = 120

    Only works with:
    - positive integers
    - zero
    """

    try:
        number = get_number()

        # Factorial does not support:
        # negative numbers
        # decimal numbers
        if number < 0 or not number.is_integer():
            raise ValueError

        result = math.factorial(
            int(number)
        )

        set_display(
            str(result)
        )

        add_history(
            f"{int(number)}!",
            result
        )

    except (
        ValueError,
        OverflowError
    ):
        show_error()


# =========================================================
# PERCENTAGE
# =========================================================
def percentage():

    safe_unary(
        "%",
        lambda x: x / 100
    )


# =========================================================
# LOG BASE 10
# =========================================================
def logarithm():

    safe_unary(
        "log",
        math.log10,
        lambda x: x > 0
    )


# =========================================================
# NATURAL LOG
# =========================================================
def natural_log():

    safe_unary(
        "ln",
        math.log,
        lambda x: x > 0
    )


# =========================================================
# TRIGONOMETRIC FUNCTIONS
# =========================================================
def trig_value(name):
    """
    Calculate:
    sin
    cos
    tan

    Supports:
    DEG
    RAD
    """

    try:
        number = get_number()

        # Convert degrees to radians
        if angle_mode == "DEG":
            angle = math.radians(number)

        else:
            angle = number

        functions = {
            "sin": math.sin,
            "cos": math.cos,
            "tan": math.tan
        }

        function = functions[name]

        # Prevent undefined tan values
        if (
            name == "tan"
            and abs(math.cos(angle)) < 1e-12
        ):
            raise ValueError

        result = function(angle)

        set_display(
            format_result(result)
        )

        add_history(
            f"{name}("
            f"{format_result(number)} "
            f"{angle_mode})",
            result
        )

    except (
        ValueError,
        OverflowError
    ):
        show_error()


# =========================================================
# CONSTANT PI
# =========================================================
def insert_pi():

    set_display(
        format_result(math.pi)
    )


# =========================================================
# CONSTANT E
# =========================================================
def insert_e():

    set_display(
        format_result(math.e)
    )


# =========================================================
# MEMORY FUNCTIONS
# =========================================================
def memory_clear():
    """
    MC = Memory Clear
    """

    global memory

    memory = 0.0

    memory_status.config(
        text="M: 0"
    )


def memory_recall():
    """
    MR = Memory Recall
    """

    set_display(
        format_result(memory)
    )


def memory_add():
    """
    M+ = Add display value to memory
    """

    global memory

    try:
        memory += get_number()

        memory_status.config(
            text=f"M: {format_result(memory)}"
        )

    except ValueError:
        show_error()


def memory_subtract():
    """
    M- = Subtract display value
    from memory
    """

    global memory

    try:
        memory -= get_number()

        memory_status.config(
            text=f"M: {format_result(memory)}"
        )

    except ValueError:
        show_error()


# =========================================================
# HISTORY FUNCTIONS
# =========================================================
def clear_history():
    """
    Delete all history.
    """

    history_items.clear()

    history_list.delete(
        0,
        END
    )


def save_history():
    """
    Save calculation history
    to TXT file.
    """

    if not history_items:

        messagebox.showinfo(
            "History",
            "No calculations to save."
        )

        return

    path = filedialog.asksaveasfilename(
        defaultextension=".txt",

        filetypes=[
            ("Text files", "*.txt"),
            ("All files", ".")
        ],

        title="Save Calculation History"
    )

    if path:

        try:

            with open(
                path,
                "w",
                encoding="utf-8"
            ) as file:

                file.write(
                    "\n".join(history_items)
                )

            messagebox.showinfo(
                "Saved",
                "Calculation history saved successfully."
            )

        except OSError:

            messagebox.showerror(
                "Error",
                "Could not save the history file."
            )


# =========================================================
# DEGREE / RADIAN TOGGLE
# =========================================================
def toggle_angle_mode():

    global angle_mode

    if angle_mode == "DEG":
        angle_mode = "RAD"

    else:
        angle_mode = "DEG"

    angle_button.config(
        text=angle_mode
    )


# =========================================================
# DARK / LIGHT THEME
# =========================================================
def toggle_theme():

    global dark_mode

    dark_mode = not dark_mode

    apply_theme()


def apply_theme():
    """
    Apply selected theme.
    """

    if dark_mode:
        t = THEMES["dark"]

    else:
        t = THEMES["light"]

    root.configure(
        bg=t["root"]
    )

    top_bar.configure(
        bg=t["root"]
    )

    display.configure(
        bg=t["display_bg"],
        fg=t["display_fg"],
        insertbackground=t["display_fg"]
    )

    main_frame.configure(
        bg=t["root"]
    )

    button_frame.configure(
        bg=t["root"]
    )

    history_frame.configure(
        bg=t["panel"]
    )

    history_title.configure(
        bg=t["panel"],
        fg=t["history_fg"]
    )

    graph_label.configure(
        bg=t["panel"],
        fg=t["history_fg"]
    )

    history_list.configure(
        bg=t["history_bg"],
        fg=t["history_fg"],
        selectbackground=t["operator"]
    )

    memory_status.configure(
        bg=t["root"],
        fg=t["history_fg"]
    )

    if dark_mode:
        theme_button.config(
            text="☀️ Light"
        )

    else:
        theme_button.config(
            text="🌙 Dark"
        )

    # Update calculator buttons
    for btn, kind in styled_buttons:

        bg = t[kind]
        fg = t["text"]

        if (
            not dark_mode
            and kind == "number"
        ):
            fg = t["display_fg"]

        btn.configure(
            bg=bg,
            fg=fg,
            activebackground=t["operator"],
            activeforeground="white"
        )


# =========================================================
# GRAPH PLOTTER
# =========================================================
def plot_graph():
    """
    Plot mathematical graph.

    Examples:
    sin(x)
    x**2
    cos(x)
    sqrt(abs(x))
    """

    if not GRAPH_AVAILABLE:

        messagebox.showerror(
            "Graph Plotter",

            "Graph plotting requires "
            "matplotlib and numpy.\n\n"

            "Install them with:\n"
            "pip install matplotlib numpy"
        )

        return

    expression = graph_entry.get().strip()

    if not expression:

        messagebox.showinfo(
            "Graph Plotter",

            "Enter a function such as:\n"
            "sin(x)\n"
            "x**2\n"
            "sqrt(abs(x))"
        )

        return

    try:

        # X-axis values
        x = np.linspace(
            -10,
            10,
            1000
        )

        # Allowed safe functions
        allowed = {
            "x": x,
            "sin": np.sin,
            "cos": np.cos,
            "tan": np.tan,
            "sqrt": np.sqrt,
            "abs": np.abs,
            "log": np.log,
              "log10": np.log10,
            "exp": np.exp,
            "pi": np.pi,
            "e": np.e
        }

        # Restrict characters
        if not re.fullmatch(
            r"[0-9a-zA-Z_+\-*/().\s]+",
            expression
        ):
            raise ValueError

        # Extract function names
        names = set(
            re.findall(
                r"[A-Za-z_]+",
                expression
            )
        )

        # Reject unknown functions
        if not names.issubset(
            allowed.keys()
        ):
            raise ValueError

        # Evaluate expression safely
        y = eval(
            expression,
            {"_builtins_": {}},
            allowed
        )

        # Handle constant graph
        if np.isscalar(y):

            y = np.full_like(
                x,
                y,
                dtype=float
            )

        # Create graph
        plt.figure(
            figsize=(8, 5)
        )

        plt.plot(
            x,
            y
        )

        plt.axhline(
            0,
            linewidth=0.8
        )

        plt.axvline(
            0,
            linewidth=0.8
        )

        plt.grid(
            True,
            alpha=0.3
        )

        plt.title(
            f"y = {expression}"
        )

        plt.xlabel("x")
        plt.ylabel("y")

        plt.tight_layout()

        plt.show()

    except Exception:

        messagebox.showerror(
            "Graph Error",

            "Invalid function.\n\n"

            "Try:\n"
            "x**2\n"
            "sin(x)\n"
            "cos(x)\n"
            "sqrt(abs(x))"
        )


# =========================================================
# KEYBOARD SUPPORT
# =========================================================
def keyboard_handler(event):
    """
    Keyboard shortcuts:

    Numbers: 0-9
    Operators: + - * /
    Enter: =
    Backspace: Delete last digit
    Escape: Clear
    """

    key = event.keysym
    char = event.char

    # Numbers
    if char in "0123456789":

        button_click(char)

        return "break"

    # Operators
    if char in "+-*/":

        get_operator(char)

        return "break"

    # Decimal
    if char == ".":

        decimal()

        return "break"

    # Enter = calculate
    if key in (
        "Return",
        "KP_Enter"
    ):

        calculate_result()

        return "break"

    # Backspace
    if key == "BackSpace":

        backspace()

        return "break"

    # Escape = clear
    if key == "Escape":

        clear_display()

        return "break"


# Bind keyboard
root.bind_all(
    "<Key>",
    keyboard_handler
)


# =========================================================
# TOP BAR
# =========================================================
t = THEMES["dark"]

top_bar = Frame(
    root,
    bg=t["root"]
)

top_bar.pack(
    fill=X,
    padx=20,
    pady=(14, 4)
)


# Memory status
memory_status = Label(
    top_bar,
    text="M: 0",
    font=("Segoe UI", 10, "bold"),
    bg=t["root"],
    fg="white"
)

memory_status.pack( side=LEFT
)


# Degree / Radian button
angle_button = Button(
    top_bar,
    text="DEG",
    font=("Segoe UI", 10, "bold"),
    bd=0,
    cursor="hand2",
    command=toggle_angle_mode
)

angle_button.pack(
    side=RIGHT,
    padx=(8, 0)
)


# Theme button
theme_button = Button(
    top_bar,
    text="☀️ Light",
    font=("Segoe UI", 10, "bold"),
    bd=0,
    cursor="hand2",
    command=toggle_theme
)

theme_button.pack(
    side=RIGHT
)


# =========================================================
# DISPLAY
# =========================================================
display = Entry(
    root,
    font=("Segoe UI", 28, "bold"),
    bg=t["display_bg"],
    fg=t["display_fg"],
    bd=0,
    relief=FLAT,
    justify=RIGHT,
    insertbackground="black"
)

display.pack(
    padx=20,
    pady=(6, 12),
    fill=X,
    ipady=16
)


# =========================================================
# MAIN FRAME
# =========================================================
main_frame = Frame(
    root,
    bg=t["root"]
)

main_frame.pack(
    fill=BOTH,
    expand=True,
    padx=14,
    pady=(0, 14)
)


# =========================================================
# BUTTON FRAME
# =========================================================
button_frame = Frame(
    main_frame,
    bg=t["root"]
)

button_frame.pack(
    side=LEFT,
    fill=BOTH,
    expand=True
)


# =========================================================
# HISTORY FRAME
# =========================================================
history_frame = Frame(
    main_frame,
    bg=t["panel"],
    width=220
)

history_frame.pack(
    side=RIGHT,
    fill=Y,
    padx=(12, 0)
)

history_frame.pack_propagate(False)


# History title
history_title = Label(
    history_frame,
    text="📋 Calculation History",
    font=("Segoe UI", 12, "bold"),
    bg=t["panel"],
    fg="white"
)

history_title.pack(
    pady=(12, 8)
)


# History list
history_list = Listbox(
    history_frame,
    font=("Consolas", 10),
    bd=0,
    bg=t["history_bg"],
    fg=t["history_fg"]
)

history_list.pack(
    fill=BOTH,
    expand=True,
    padx=10,
    pady=(0, 8)
)


# =========================================================
# HISTORY BUTTONS
# =========================================================
history_actions = Frame(
    history_frame,
    bg=t["panel"]
)

history_actions.pack(
    fill=X,
    padx=8,
    pady=(0, 8)
)


Button(
    history_actions,
    text="Save",
    command=save_history,
    bd=0,
    cursor="hand2"
).pack(
    side=LEFT,
    expand=True,
    fill=X,
    padx=2
)


Button(
    history_actions,
    text="Clear",
    command=clear_history,
    bd=0,
    cursor="hand2"
).pack(
    side=LEFT,
    expand=True,
    fill=X,
    padx=2
)


# =========================================================
# GRAPH SECTION
# =========================================================
graph_label = Label(
    history_frame,
    text="📊 Graph: y = f(x)",
    font=("Segoe UI", 10, "bold"),
    bg=t["panel"],
    fg="white"
)

graph_label.pack(
    pady=(4, 3)
)


graph_entry = Entry(history_frame,
    font=("Segoe UI", 10)
)

graph_entry.pack(
    fill=X,
    padx=10,
    pady=3
)


# Default example
graph_entry.insert(
    0,
    "sin(x)"
)


Button(
    history_frame,
    text="Plot Graph",
    command=plot_graph,
    bd=0,
    cursor="hand2"
).pack(
    fill=X,
    padx=10,
    pady=(3, 12)
)


# =========================================================
# BUTTON CREATION FUNCTION
# =========================================================
styled_buttons = []


def create_button(
    text,
    row,
    column,
    command,
    kind="number",
    columnspan=1
):
    """
    Create calculator button
    with hover effect.
    """

    btn = Button(
        button_frame,
        text=text,
        font=("Segoe UI", 13, "bold"),
        relief=FLAT,
        bd=0,
        cursor="hand2",
        command=command
    )

    btn.grid(
        row=row,
        column=column,
        columnspan=columnspan,
        sticky="nsew",
        padx=4,
        pady=4,
        ipadx=3,
        ipady=8
    )

    # Hover effect
    def on_enter(event, button=btn):
        button.configure(
            relief=RAISED
        )

    def on_leave(event, button=btn):
        button.configure(
            relief=FLAT
        )

    btn.bind(
        "<Enter>",
        on_enter
    )

    btn.bind(
        "<Leave>",
        on_leave
    )

    styled_buttons.append(
        (btn, kind)
    )

    return btn


# =========================================================
# RESPONSIVE GRID
# =========================================================
for i in range(9):

    button_frame.grid_rowconfigure(
        i,
        weight=1
    )


for j in range(4):

    button_frame.grid_columnconfigure(
        j,
        weight=1
    )


# =========================================================
# MEMORY BUTTON ROW
# =========================================================
create_button(
    "MC",
    0,
    0,
    memory_clear,
    "function"
)

create_button(
    "MR",
    0,
    1,
    memory_recall,
    "function"
)

create_button(
    "M+",
    0,
    2,
    memory_add,
    "function"
)

create_button(
    "M-",
    0,
    3,
    memory_subtract,
    "function"
)


# =========================================================
# SCIENTIFIC ROW 1
# =========================================================
create_button(
    "sin",
    1,
    0,
    lambda: trig_value("sin"),
    "function"
)

create_button(
    "cos",
    1,
    1,
    lambda: trig_value("cos"),
    "function"
)

create_button(
    "tan",
    1,
    2,
    lambda: trig_value("tan"),
    "function"
)

create_button(
    "√",
    1,
    3,
    square_root,
    "operator"
)


# =========================================================
# SCIENTIFIC ROW 2
# =========================================================
create_button(
    "log",
    2,
    0,
    logarithm,
    "function"
)

create_button(
    "ln",
    2,
    1,
    natural_log,
    "function"
)

create_button(
    "x²",
    2,
    2,
    square,
    "function"
)

create_button(
    "xʸ",
    2,
    3,  lambda: get_operator("^"),
    "operator"
)


# =========================================================
# SCIENTIFIC ROW 3
# =========================================================
create_button(
    "π",
    3,
    0,
    insert_pi,
    "function"
)

create_button(
    "e",
    3,
    1,
    insert_e,
    "function"
)

create_button(
    "n!",
    3,
    2,
    factorial,
    "function"
)

create_button(
    "%",
    3,
    3,
    percentage,
    "operator"
)


# =========================================================
# NUMBER ROW 7 8 9
# =========================================================
create_button(
    "7",
    4,
    0,
    lambda: button_click("7")
)

create_button(
    "8",
    4,
    1,
    lambda: button_click("8")
)

create_button(
    "9",
    4,
    2,
    lambda: button_click("9")
)

create_button(
    "/",
    4,
    3,
    lambda: get_operator("/"),
    "operator"
)


# =========================================================
# NUMBER ROW 4 5 6
# =========================================================
create_button(
    "4",
    5,
    0,
    lambda: button_click("4")
)

create_button(
    "5",
    5,
    1,
    lambda: button_click("5")
)

create_button(
    "6",
    5,
    2,
    lambda: button_click("6")
)

create_button(
    "*",
    5,
    3,
    lambda: get_operator("*"),
    "operator"
)


# =========================================================
# NUMBER ROW 1 2 3
# =========================================================
create_button(
    "1",
    6,
    0,
    lambda: button_click("1")
)

create_button(
    "2",
    6,
    1,
    lambda: button_click("2")
)

create_button(
    "3",
    6,
    2,
    lambda: button_click("3")
)

create_button(
    "-",
    6,
    3,
    lambda: get_operator("-"),
    "operator"
)


# =========================================================
# NUMBER ROW C 0 . +
# =========================================================
create_button(
    "C",
    7,
    0,
    clear_display,
    "danger"
)

create_button(
    "0",
    7,
    1,
    lambda: button_click("0")
)

create_button(
    ".",
    7,
    2,
    decimal
)

create_button(
    "+",
    7,
    3,
    lambda: get_operator("+"),
    "operator"
)


# =========================================================
# FINAL ROW
# =========================================================
create_button(
    "⌫",
    8,
    0,
    backspace,
    "warning"
)

create_button(
    "±",
    8,
    1,
    plus_minus,
    "warning"
)

create_button(
    "=",
    8,
    2,
    calculate_result,
    "equal",
    columnspan=2
)


# =========================================================
# APPLY DEFAULT THEME
# =========================================================
apply_theme()


# Put keyboard focus on display
display.focus_set()


# =========================================================
# RUN APPLICATION
# =========================================================
root.mainloop()