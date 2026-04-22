import customtkinter as ctk
import json
import os

# Настройки стиля
ctk.set_appearance_mode("dark")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("dark-blue")  # Themes: "blue" (standard), "green", "dark-blue"

class TodoApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Настройка окна
        self.title(" ✨ Premium Task Manager SE")
        self.geometry("900x650") # Увеличили окно для боковой панели

        # Данные
        self.tasks = self.load_tasks()

        # Конфигурация сетки (Grid)
        self.grid_columnconfigure(1, weight=1) # Основной контент расширяется
        self.grid_rowconfigure(0, weight=1) # Высота на все окно

        self.setup_ui()
        self.refresh_list()

    def setup_ui(self):
        # 1. БОКОВАЯ ПАНЕЛЬ (Sidebar)
        self.sidebar_frame = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1) # Отступ снизу

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="SE To-Do", font=("Helvetica", 26, "bold"), text_color="#3b8ed0")
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.sub_logo_label = ctk.CTkLabel(self.sidebar_frame, text="v 1.0", font=("Helvetica", 12), text_color="gray")
        self.sub_logo_label.grid(row=1, column=0, padx=20, pady=(0, 20))

        # Статистика в сайдбаре
        self.stats_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        self.stats_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")

        self.total_label = ctk.CTkLabel(self.stats_frame, text="Всего задач:", font=("Helvetica", 14))
        self.total_label.pack(anchor="w")
        self.total_count = ctk.CTkLabel(self.stats_frame, text="0", font=("Helvetica", 20, "bold"))
        self.total_count.pack(anchor="w", pady=(0, 10))

        self.done_label = ctk.CTkLabel(self.stats_frame, text="Выполнено:", font=("Helvetica", 14))
        self.done_label.pack(anchor="w")
        self.done_count = ctk.CTkLabel(self.stats_frame, text="0", font=("Helvetica", 20, "bold"), text_color="#2ecc71")
        self.done_count.pack(anchor="w")

        # Переключатель темы (для UX бонуса)
        self.appearance_mode_label = ctk.CTkLabel(self.sidebar_frame, text="Тема:", anchor="w")
        self.appearance_mode_label.grid(row=5, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionemenu = ctk.CTkOptionMenu(self.sidebar_frame, values=["Dark", "Light", "System"],
                                                                       command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=6, column=0, padx=20, pady=(10, 20))
        self.appearance_mode_optionemenu.set("Dark")


        # 2. ОСНОВНОЙ КОНТЕНТ
        self.main_label = ctk.CTkLabel(self, text="📝 To - Do list", font=("Helvetica", 36, "bold"))
        self.main_label.grid(row=0, column=1, padx=30, pady=(30, 10), sticky="w")

        self.descr_label = ctk.CTkLabel(self, text="Управляйте вашими задачами эффективно.", font=("Helvetica", 16), text_color="gray")
        self.descr_label.grid(row=1, column=1, padx=30, pady=(0, 30), sticky="w")

        # Панель ввода задач
        self.input_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.input_frame.grid(row=2, column=1, padx=30, pady=10, sticky="ew")
        self.input_frame.grid_columnconfigure(0, weight=1)

        self.entry = ctk.CTkEntry(self.input_frame, placeholder_text="Что планируете сделать сегодня?", height=50, corner_radius=15, font=("Helvetica", 14))
        self.entry.grid(row=0, column=0, padx=(0, 15), sticky="ew")

        self.add_button = ctk.CTkButton(self.input_frame, text="➕ Добавить", command=self.add_task, height=50, width=150, corner_radius=15, font=("Helvetica", 14, "bold"))
        self.add_button.grid(row=0, column=1, sticky="nsew")

        # Скроллящаяся область для задач
        self.scrollable_frame = ctk.CTkScrollableFrame(self, label_text="Ваши текущие задачи", label_font=("Helvetica", 14, "bold"), fg_color="transparent")
        self.scrollable_frame.grid(row=3, column=1, padx=30, pady=20, sticky="nsew")
        self.scrollable_frame.grid_columnconfigure(0, weight=1) # Карточки на всю ширину


    def add_task(self):
        task_text = self.entry.get()
        if task_text.strip():
            self.tasks.append({"text": task_text, "completed": False})
            self.entry.delete(0, 'end')
            self.save_tasks()
            self.refresh_list()

    def refresh_list(self):
        # Очистка
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        # Статистика
        total = len(self.tasks)
        done = sum(1 for task in self.tasks if task["completed"])
        self.total_count.configure(text=str(total))
        self.done_count.configure(text=str(done))

        # Отрисовка задач в виде карточек
        for index, task in enumerate(self.tasks):
            # КАРТОЧКА ЗАДАЧИ
            card_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="#212121", corner_radius=12, height=60)
            card_frame.grid(row=index, column=0, pady=8, padx=5, sticky="ew")
            card_frame.grid_columnconfigure(0, weight=1)

            # Текст задачи (Чекбокс)
            task_font = ("Helvetica", 15)
            check = ctk.CTkCheckBox(card_frame, text=task["text"], font=task_font, corner_radius=6, command=lambda i=index: self.toggle_task(i))
            if task["completed"]:
                check.select()
                # Изменяем шрифт для выполненных (UX бонус!)
                check.configure(font=("Helvetica", 15, "overstrike"), text_color="gray")
            check.grid(row=0, column=0, padx=15, pady=15, sticky="w")

            # Кнопка удаления
            delete_btn = ctk.CTkButton(card_frame, text="✕", width=35, height=35, corner_radius=8, fg_color="#444444", text_color="#e74c3c", hover_color="#2a2a2a", font=("Helvetica", 12, "bold"), command=lambda i=index: self.delete_task(i))
            delete_btn.grid(row=0, column=1, padx=15)

    def toggle_task(self, index):
        self.tasks[index]["completed"] = not self.tasks[index]["completed"]
        self.save_tasks()
        self.refresh_list() # Обновляем, чтобы применить overstrike шрифт

    def delete_task(self, index):
        del self.tasks[index]
        self.save_tasks()
        self.refresh_list()

    # Вспомогательные функции
    def change_appearance_mode_event(self, new_appearance_mode: str):
        ctk.set_appearance_mode(new_appearance_mode)

    def save_tasks(self):
        with open("tasks.json", "w", encoding="utf-8") as f:
            json.dump(self.tasks, f, ensure_ascii=False, indent=4)

    def load_tasks(self):
        if os.path.exists("tasks.json"):
            try:
                with open("tasks.json", "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                return []
        return []

if __name__ == "__main__":
    app = TodoApp()
    app.mainloop()