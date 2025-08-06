import tkinter as tk
import tkinter.messagebox as msgbox
from PIL import Image, ImageTk
import pygame
import string
import random

pygame.mixer.init()
pygame.mixer.music.load("bg.mp3")
pygame.mixer.music.play(-1)

is_audio_on = True
hints_left = 2
score = 0
high_score = 0
gems = 0
word = "PYTHON"
guessed = []
time_left = 60
is_game_running = False
timer_id = None
letter_buttons = []
is_dark_mode = False
difficulty = "Easy"

words_by_difficulty = {
    "Easy": ["DOOR", "SUN", "CAR", "BOOK", "FISH"],
    "Medium": ["PYTHON", "PLANET", "LAPTOP", "JUNGLE", "BANANA"],
    "Hard": ["COMPLEXITY", "ELEPHANTINE", "PSYCHOLOGY", "HIERARCHY", "MICROSCOPE"]
}

welcome_label = None
audio_toggle_button = None
new_game_button = None
instructions_button = None
high_scores_button = None
settings_button = None
difficulty_button = None
start_button = None
stop_button = None
resume_button = None
hint_button = None
gems_label = None
timer_text_label = None


def toggle_audio():
    global is_audio_on
    if is_audio_on:
        pygame.mixer.music.pause()
        audio_btn.config(text="Audio Off 🔇")
        is_audio_on = False
    else:
        pygame.mixer.music.unpause()
        audio_btn.config(text="Audio On 🔊")
        is_audio_on = True

def open_difficulty_window():
    difficulty_window = tk.Toplevel()
    difficulty_window.title("Select Difficulty")
    difficulty_window.geometry("300x250")
    difficulty_window.configure(bg="#ecf0f1")

    tk.Label(difficulty_window, text="Choose Difficulty Level", font=("Arial", 16, "bold"), bg="#ecf0f1", fg="#34495E").pack(pady=20)

    def select_difficulty(level):
        global difficulty
        difficulty = level
        difficulty_window.destroy()

    tk.Button(difficulty_window, text="Easy", font=("Arial", 14), bg="#D3D3D3", width=15, command=lambda: select_difficulty("Easy")).pack(pady=5)
    tk.Button(difficulty_window, text="Medium", font=("Arial", 14), bg="#778899", width=15, command=lambda: select_difficulty("Medium")).pack(pady=5)
    tk.Button(difficulty_window, text="Hard", font=("Arial", 14), bg="#7B7E7F", width=15, command=lambda: select_difficulty("Hard")).pack(pady=5)

def open_instructions():
    instructions_window = tk.Toplevel()
    instructions_window.title("Instructions")
    instructions_window.geometry("400x300")
    instructions_window.configure(bg="#ecf0f1")
    tk.Label(instructions_window, text="Hangman Instructions", font=("Arial", 10, "bold"), fg="#2c3e50", bg="#ecf0f1").pack(pady=14)
    msg = (
        "1. Guess the word by clicking letters.\n"
        "2. You have limited time of one minute.\n"
        "3. You have only two hints in each game.\n"
        "4. Each wrong guess reduces chances.\n"
        "5. You win if you guess the word\n before time runs out!"
    )
    tk.Label(instructions_window, text=msg, font=("Arial", 16), bg="#ecf0f1", fg="black", justify="center").pack(pady=20)

def open_settings():
    settings_window = tk.Toplevel()
    settings_window.title("Settings")
    settings_window.geometry("300x200")
    settings_window.configure(bg="#ecf0f1")

    tk.Label(settings_window, text="Choose Theme", font=("Arial", 16, "bold"), bg="#ecf0f1", fg="#2c3e50").pack(pady=20)

    def toggle_theme(mode):
        global is_dark_mode
        is_dark_mode = (mode == "Dark")
        apply_theme()
        msgbox.showinfo("Theme Changed", f"{mode} mode activated.")
        settings_window.destroy()

    tk.Button(settings_window, text="Dark Mode", font=("Arial", 14), bg="#2c3e50", fg="white", width=15, command=lambda: toggle_theme("Dark")).pack(pady=5)
    tk.Button(settings_window, text="Light Mode", font=("Arial", 14), bg="#ecf0f1", fg="black", width=15, command=lambda: toggle_theme("Light")).pack(pady=5)

def use_hint():
    global hints_left
    if hints_left > 0:
        for i, ch in enumerate(word):
            if ch not in guessed:
                guessed.append(ch)
                update_word_display()
                hints_left -= 1
                hint_btn.config(text=f"Hint ({hints_left})")
                check_win_condition()
                break

def update_word_display():
    display = " ".join([ch if ch in guessed else "_" for ch in word])
    word_label.config(text=display)

def update_score():
    score_label.config(text=f"Score: {score}")
    high_score_label.config(text=f"High Score: {max(score, high_score)}")

def update_timer():
    global time_left, timer_id
    if is_game_running and time_left > 0:
        time_left -= 1
        timer_bar.coords(timer_fill, 0, 0, time_left * 2, 20)
        timer_text.config(text=f"{time_left}s")
        timer_id = root.after(1000, update_timer)
    elif time_left == 0:
        end_game_lost()

def letter_click(letter):
    global score
    if letter not in guessed:
        guessed.append(letter)
        if letter in word:
            score += 10
        else:
            score -= 2
        update_word_display()
        update_score()
        check_win_condition()

def check_win_condition():
    global high_score
    if "_" not in [ch if ch in guessed else "_" for ch in word]:
        stop_game()
        if score > high_score:
            high_score = score
        update_score()
        msgbox.showinfo("🎉 Congratulations", "You won!")

def end_game_lost():
    stop_game()
    msgbox.showinfo("⏰ Time's Up", "You lost! Better luck next time.")

def resume_game():
    global is_game_running
    if not is_game_running:
        is_game_running = True
        update_timer()
        for btn in letter_buttons:
            btn.config(state="normal")

def stop_game():
    global is_game_running, timer_id
    is_game_running = False
    if timer_id:
        root.after_cancel(timer_id)
    for btn in letter_buttons:
        btn.config(state="disabled")

def start_game():
    global is_game_running, time_left, guessed, score, word, hints_left
    guessed = []
    time_left = 90
    score = 0
    hints_left = 2
    is_game_running = True
    word = random.choice(words_by_difficulty[difficulty])
    main_frame.pack_forget()

    bg_color = "#000000" if is_dark_mode else "#ecf0f1"
    game_frame.configure(bg=bg_color)
    for widget in game_frame.winfo_children():
        widget.configure(bg=bg_color)
        for subwidget in widget.winfo_children():
            subwidget.configure(bg=bg_color)

    game_frame.pack(expand=True, fill="both")
    update_word_display()
    update_score()
    update_timer()
    hint_btn.config(text=f"Hint ({hints_left})")
    for btn in letter_buttons:
        btn.config(state="normal")

def back():
    stop_game()
    game_frame.pack_forget()
    main_frame.pack(expand=True)

def show_high_scores():
    msgbox.showinfo("High Scores", f"High Score: {high_score}")

def apply_theme():
    bg_color = "#2c3e50" if is_dark_mode else "#ecf0f1"
    fg_color = "white" if is_dark_mode else "black"
    
    root.configure(bg="black")

    for btn in letter_buttons:
        btn.configure(bg="#34495e" if is_dark_mode else "#f5f5f5",
                      fg="white" if is_dark_mode else "#2c3e50")

    for btn in [new_game_button, instructions_button, high_scores_button, settings_button, difficulty_button, audio_toggle_button]:
        btn.configure(bg="#34495e" if is_dark_mode else "#7B7E7F",
                      fg="white" if is_dark_mode else "white")

    if welcome_label:
        welcome_label.configure(fg="black")

    if word_label:
        word_label.configure(bg=bg_color, fg=fg_color)
    if timer_text_label:
        timer_text_label.configure(bg=bg_color, fg=fg_color)
    if score_label:
        score_label.configure(bg=bg_color, fg=fg_color)
    if high_score_label:
        high_score_label.configure(bg=bg_color, fg=fg_color)
    if gems_label:
        gems_label.configure(bg=bg_color, fg=fg_color)

    for widget in game_frame.winfo_children():
        for child in widget.winfo_children():
            if isinstance(child, tk.Button):
                child.configure(bg="#7f8c8d" if is_dark_mode else "#bdc3c7",
                                fg="white" if is_dark_mode else "black")


def main():
    global root, main_frame, game_frame, word_label, timer_bar, timer_fill, timer_text
    global audio_btn, hint_btn, score_label, high_score_label, gems_label, timer_text_label

    root = tk.Tk()
    root.title("Hangman Game")
    root.geometry("900x650")

    bg_img = Image.open("bg.png")
    bg_img = bg_img.resize((2500, 1300), Image.Resampling.LANCZOS)
    bg_photo = ImageTk.PhotoImage(bg_img)
    bg_label = tk.Label(root, image=bg_photo)
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)
    root.bg_photo = bg_photo

    global welcome_label
    main_frame = tk.Frame(root, bg="#dddddd")
    main_frame.pack(expand=True)

    welcome_label = tk.Label(main_frame, text="Welcome to Hangman", font=("Arial", 40, "bold"), bg="#dddddd", fg="black")
    welcome_label.pack(pady=(0, 30))

    btn_style = {
        "font": ("Arial", 18, "bold"), "width": 17, "bg": "#7B7E7F",
        "fg": "white", "activebackground": "#d3d3d3", "cursor": "hand2"
    }

    global new_game_button, instructions_button, high_scores_button, settings_button, difficulty_button, audio_toggle_button
    new_game_button = tk.Button(main_frame, text="New Game", command=start_game, **btn_style)
    new_game_button.pack(pady=7)

    instructions_button = tk.Button(main_frame, text="Instructions", command=open_instructions, **btn_style)
    instructions_button.pack(pady=7)

    high_scores_button = tk.Button(main_frame, text="High Scores", command=show_high_scores, **btn_style)
    high_scores_button.pack(pady=7)

    settings_button = tk.Button(main_frame, text="Settings", command=open_settings, **btn_style)
    settings_button.pack(pady=7)

    difficulty_button = tk.Button(main_frame, text="Difficulty", command=open_difficulty_window, **btn_style)
    difficulty_button.pack(pady=7)

    audio_toggle_button = tk.Button(main_frame, text="Audio On 🔊", command=toggle_audio, **btn_style)
    audio_toggle_button.pack(pady=7)
    audio_btn = audio_toggle_button

    game_frame = tk.Frame(root, bg="#ecf0f1")
    top_frame = tk.Frame(game_frame, bg="#ecf0f1")
    top_frame.pack(fill="x", pady=10)

    score_label = tk.Label(top_frame, text=f"Score: {score}", font=("Arial", 14, "bold"), bg="#ecf0f1")
    score_label.pack(side="left", padx=20)

    high_score_label = tk.Label(top_frame, text=f"High Score: {high_score}", font=("Arial", 14, "bold"), bg="#ecf0f1")
    high_score_label.pack(side="left")

    gems_label = tk.Label(top_frame, text=f"💎 {gems}", font=("Arial", 14, "bold"), bg="#ecf0f1")
    gems_label.pack(side="right", padx=20)

    word_label = tk.Label(game_frame, text="", font=("Arial", 32, "bold"), bg="#ecf0f1")
    word_label.pack(pady=(10, 20))

    timer_frame = tk.Frame(game_frame, bg="#ecf0f1")
    timer_frame.pack()
    timer_canvas = tk.Canvas(timer_frame, width=180, height=20, bg="#ecf0f1", highlightthickness=0)
    timer_canvas.pack()
    timer_fill = timer_canvas.create_rectangle(0, 0, 180, 20, fill="light green")
    timer_text = tk.Label(timer_frame, text="90s", font=("Arial", 12, "bold"), bg="#ecf0f1")
    timer_text.pack()
    timer_bar = timer_canvas
    timer_text_label = timer_text

    letters_frame = tk.Frame(game_frame, bg="#ecf0f1")
    letters_frame.pack(pady=40)
    letters = list(string.ascii_uppercase)
    for i in range(4):
        row = tk.Frame(letters_frame, bg="#ecf0f1")
        row.pack()
        for j in range(7 if i < 3 else 5):
            index = i * 7 + j
            if index < len(letters):
                btn = tk.Button(row, text=letters[index], font=("Arial", 14, "bold"), width=5, height=2,
                                bg="#2c3e50", fg="white", command=lambda l=letters[index]: letter_click(l))
                btn.pack(side="left", padx=3, pady=3)
                letter_buttons.append(btn)

    control_frame = tk.Frame(game_frame, bg="#ecf0f1")
    control_frame.pack(pady=10)

    tk.Button(control_frame, text="Back", font=("Arial", 14, "bold"), bg="#bdc3c7", fg="black", width=10, command=back).pack(side="left", padx=10)
    tk.Button(control_frame, text="Resume", font=("Arial", 14, "bold"), bg="#bdc3c7", fg="black", width=10, command=resume_game).pack(side="left", padx=10)
    tk.Button(control_frame, text="Stop", font=("Arial", 14, "bold"), bg="#bdc3c7", fg="black", width=10, command=stop_game).pack(side="left", padx=10)

    hint_btn = tk.Button(control_frame, text=f"Hint ({hints_left})", font=("Arial", 14, "bold"), bg="#7f8c8d", fg="black", width=10, command=use_hint)
    hint_btn.pack(side="left", padx=10)

    root.mainloop()


if __name__ == "__main__":
    main()
