import tkinter as tk
from tkinter import ttk
from plyer import notification
import time
from datetime import datetime, timedelta

class RoundedButton(tk.Canvas):
    def __init__(self, parent, text, command, width=120, height=35, corner_radius=10, bg='#4CAF50', fg='white', **kwargs):
        super().__init__(parent, width=width, height=height, bg=parent["bg"], highlightthickness=0, **kwargs)
        self.command = command
        self.bg = bg
        self.text = text
        self.fg = fg
        
        # Créer le fond du bouton
        self.rect_id = self.create_rounded_rect(0, 0, width, height, corner_radius, self.bg)
        # Créer le texte
        self.text_id = self.create_text(width/2, height/2, text=text, fill=fg, font=('Arial', 10, 'bold'))
        
        # Bind events
        self.bind('<Button-1>', self._on_click)
        self.bind('<Enter>', lambda e: self._on_hover(True))
        self.bind('<Leave>', lambda e: self._on_hover(False))

    def create_rounded_rect(self, x1, y1, x2, y2, radius, color):
        points = [x1+radius, y1,
                x2-radius, y1,
                x2, y1,
                x2, y1+radius,
                x2, y2-radius,
                x2, y2,
                x2-radius, y2,
                x1+radius, y2,
                x1, y2,
                x1, y2-radius,
                x1, y1+radius,
                x1, y1]
        return self.create_polygon(points, smooth=True, fill=color)

    def _on_click(self, event):
        if self.command:
            self.command()

    def _on_hover(self, entering):
        # Assombrir le bouton au survol
        color = self._adjust_color(self.bg, -20) if entering else self.bg
        self.itemconfig(self.rect_id, fill=color)  # Modifier uniquement la couleur du rectangle

    def _adjust_color(self, color, amount):
        r = int(color[1:3], 16) + amount
        g = int(color[3:5], 16) + amount
        b = int(color[5:7], 16) + amount
        r = min(max(r, 0), 255)
        g = min(max(g, 0), 255)
        b = min(max(b, 0), 255)
        return f'#{r:02x}{g:02x}{b:02x}'

    def configure(self, **kwargs):
        if 'state' in kwargs:
            if kwargs['state'] == 'disabled':
                self.itemconfig(self.rect_id, fill='#cccccc')
                self.itemconfig(self.text_id, fill='#666666')
            else:
                self.itemconfig(self.rect_id, fill=self.bg)
                self.itemconfig(self.text_id, fill=self.fg)

class PomodoroTimer:
    def __init__(self, root):
        self.root = root
        self.root.title("Pomodoro Timer")
        self.root.geometry("300x400")
        self.root.configure(bg='#F0F2F5')

        # Variables
        self.timer_running = False
        self.current_time = 0
        self.session_count = 0
        self.current_session = 0
        self.pomodoro_count = 0
        self.mode = "30/10"

        # Frame principal avec padding et couleur de fond
        main_frame = tk.Frame(root, bg='#F0F2F5', padx=20, pady=20)
        main_frame.pack(expand=True, fill='both')

        # Titre stylisé
        title_label = tk.Label(main_frame, text="POMODORO", font=('Arial', 20, 'bold'),
                             bg='#F0F2F5', fg='#2C3E50')
        title_label.pack(pady=(0, 20))

        # Frame pour les modes
        mode_frame = tk.Frame(main_frame, bg='#F0F2F5')
        mode_frame.pack(fill='x', pady=(0, 15))

        # Style personnalisé pour les Radiobuttons
        self.mode_var = tk.StringVar(value="30/10")
        styles = {'bg': '#F0F2F5', 'font': ('Arial', 10), 'selectcolor': '#4CAF50'}
        
        tk.Radiobutton(mode_frame, text="30min/10min", variable=self.mode_var,
                      value="30/10", command=self.change_mode,
                      **styles).pack(side='left', padx=10)
        tk.Radiobutton(mode_frame, text="20min/5min", variable=self.mode_var,
                      value="20/5", command=self.change_mode,
                      **styles).pack(side='right', padx=10)

        # Frame pour le nombre de sessions
        session_frame = tk.Frame(main_frame, bg='#F0F2F5')
        session_frame.pack(fill='x', pady=(0, 20))
        
        tk.Label(session_frame, text="Sessions:", font=('Arial', 10),
                bg='#F0F2F5', fg='#2C3E50').pack(side='left', padx=(0, 10))
        
        self.session_var = tk.StringVar(value="1")
        entry_style = {'font': ('Arial', 10), 'width': 5, 'justify': 'center'}
        self.session_entry = tk.Entry(session_frame, textvariable=self.session_var,
                                    **entry_style)
        self.session_entry.pack(side='left')

        # Timer display avec fond blanc et coins arrondis
        timer_frame = tk.Frame(main_frame, bg='white', padx=20, pady=20)
        timer_frame.pack(fill='x', pady=(0, 20))
        timer_frame.pack_propagate(False)
        timer_frame.configure(height=100)

        self.time_label = tk.Label(timer_frame, text="00:00", font=('Arial', 48, 'bold'),
                                 bg='white', fg='#2C3E50')
        self.time_label.pack(expand=True)

        # Status label
        self.status_label = tk.Label(main_frame, text="Prêt à commencer",
                                   font=('Arial', 12), bg='#F0F2F5', fg='#2C3E50')
        self.status_label.pack(pady=(0, 20))

# Boutons
        button_frame = tk.Frame(main_frame, bg='#F0F2F5')
        button_frame.pack(fill='x', pady=(0, 20))

        # Configuration de la grille pour centrer les boutons
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, minsize=20)  # espace entre les boutons
        button_frame.grid_columnconfigure(2, weight=1)

        # Création des boutons avec la même taille
        button_width = 130
        button_height = 40

        self.start_button = RoundedButton(
            button_frame, 
            "Démarrer", 
            self.start_timer, 
            width=button_width, 
            height=button_height, 
            bg='#4CAF50'
        )
        self.start_button.grid(row=0, column=0, sticky='e')

        self.stop_button = RoundedButton(
            button_frame, 
            "Arrêter", 
            self.stop_timer, 
            width=button_width, 
            height=button_height, 
            bg='#F44336'
        )
        self.stop_button.grid(row=0, column=2, sticky='w')
        # Progress label
        self.progress_label = tk.Label(main_frame, text="Session 0/0 - Pomodori 0/4",
                                     font=('Arial', 10), bg='#F0F2F5', fg='#666666')
        self.progress_label.pack()

    def change_mode(self):
        self.mode = self.mode_var.get()
        self.update_status_label("Prêt à commencer")

    def update_time_display(self):
        minutes = self.current_time // 60
        seconds = self.current_time % 60
        self.time_label.config(text=f"{minutes:02d}:{seconds:02d}")

    def update_status_label(self, text):
        self.status_label.config(text=text)

    def send_notification(self, title, message):
        notification.notify(
            title=title,
            message=message,
            timeout=10
        )

    def start_timer(self):
        if not self.timer_running:
            try:
                self.session_count = int(self.session_var.get())
                if self.session_count <= 0:
                    raise ValueError
            except ValueError:
                self.update_status_label("Veuillez entrer un nombre valide de sessions")
                return

            self.timer_running = True
            self.start_button.configure(state='disabled')
            self.current_session = 1
            self.pomodoro_count = 0
            self.run_pomodoro()

    def stop_timer(self):
        self.timer_running = False
        self.start_button.configure(state='normal')
        self.update_status_label("Timer arrêté")
        self.time_label.config(text="00:00")
        self.progress_label.config(text="Session 0/0 - Pomodori 0/4")

    def run_pomodoro(self):
        if not self.timer_running:
            return

        # Définir la durée en fonction du mode
        if self.mode == "30/10":
            work_time = 30 * 60
            short_break = 10 * 60
            long_break = 30 * 60
        else:  # mode "20/5"
            work_time = 20 * 60
            short_break = 5 * 60
            long_break = 20 * 60

        # Déterminer la phase actuelle
        if self.pomodoro_count % 4 == 0 and self.pomodoro_count != 0:
            # Grande pause
            self.update_status_label("Pause café!")
            self.current_time = long_break
        elif self.pomodoro_count % 2 == 1:
            # Petite pause
            self.update_status_label("Une petite pause")
            self.current_time = short_break
        else:
            # Travail
            self.update_status_label("Au travail!")
            self.current_time = work_time

        self.countdown()

    def countdown(self):
        if not self.timer_running:
            return

        if self.current_time <= 0:
            self.send_notification("Pomodoro", f"Fin de {self.status_label.cget('text')}")

            # Transition vers la phase suivante
            if "travail" in self.status_label.cget('text').lower():
                self.pomodoro_count += 1

            if self.pomodoro_count == 4 and self.current_session < self.session_count:
                self.current_session += 1
                self.pomodoro_count = 0
            elif self.pomodoro_count == 4 and self.current_session == self.session_count:
                self.stop_timer()
                return

            self.run_pomodoro()
            return

        # Mise à jour de l'affichage
        self.update_time_display()
        self.progress_label.config(
            text=f"Session {self.current_session}/{self.session_count} - "
                 f"Pomodori {self.pomodoro_count}/4"
        )
        self.current_time -= 1
        self.root.after(1000, self.countdown)

if __name__ == "__main__":
    root = tk.Tk()
    app = PomodoroTimer(root)
    root.mainloop()