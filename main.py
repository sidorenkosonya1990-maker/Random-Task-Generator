import tkinter as tk
from tkinter import ttk, messagebox
import random
import json
import os
from datetime import datetime

class RandomTaskGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Random Task Generator")
        self.root.geometry("600x500")
        self.root.resizable(True, True)
        
        # Предопределенные задачи
        self.tasks = {
            "учёба": [
                "Прочитать статью",
                "Решить 5 задач",
                "Посмотреть обучающее видео",
                "Написать конспект",
                "Выучить 10 новых слов"
            ],
            "спорт": [
                "Сделать зарядку",
                "Пробежать 3 км",
                "Сделать 20 отжиманий",
                "Растяжка 15 минут",
                "Приседания 30 раз"
            ],
            "работа": [
                "Проверить почту",
                "Составить план на день",
                "Подготовить отчёт",
                "Позвонить клиенту",
                "Обновить документацию"
            ]
        }
        
        # История задач
        self.history = []
        
        # Файл для сохранения истории
        self.history_file = "task_history.json"
        
        # Загрузка истории при запуске
        self.load_history()
        
        # Создание интерфейса
        self.create_widgets()
        
    def create_widgets(self):
        # Главный фрейм
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Заголовок
        title_label = ttk.Label(main_frame, text="Генератор случайных задач", 
                                font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=10)
        
        # Фрейм для фильтрации
        filter_frame = ttk.LabelFrame(main_frame, text="Фильтр по типу задачи", padding="10")
        filter_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # Выбор типа задачи
        ttk.Label(filter_frame, text="Тип задачи:").grid(row=0, column=0, padx=5)
        self.filter_var = tk.StringVar(value="все")
        filter_combo = ttk.Combobox(filter_frame, textvariable=self.filter_var, 
                                    values=["все", "учёба", "спорт", "работа"], 
                                    state="readonly", width=15)
        filter_combo.grid(row=0, column=1, padx=5)
        filter_combo.bind("<<ComboboxSelected>>", self.update_history_display)
        
        # Кнопка генерации
        generate_btn = ttk.Button(filter_frame, text="Сгенерировать задачу", 
                                  command=self.generate_task)
        generate_btn.grid(row=0, column=2, padx=20)
        
        # Фрейм для добавления новой задачи
        add_frame = ttk.LabelFrame(main_frame, text="Добавить новую задачу", padding="10")
        add_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        # Поле ввода новой задачи
        ttk.Label(add_frame, text="Задача:").grid(row=0, column=0, padx=5)
        self.new_task_entry = ttk.Entry(add_frame, width=30)
        self.new_task_entry.grid(row=0, column=1, padx=5)
        
        # Выбор типа для новой задачи
        ttk.Label(add_frame, text="Тип:").grid(row=0, column=2, padx=5)
        self.task_type_var = tk.StringVar(value="учёба")
        type_combo = ttk.Combobox(add_frame, textvariable=self.task_type_var, 
                                 values=["учёба", "спорт", "работа"], 
                                 state="readonly", width=10)
        type_combo.grid(row=0, column=3, padx=5)
        
        # Кнопка добавления
        add_btn = ttk.Button(add_frame, text="Добавить", command=self.add_task)
        add_btn.grid(row=0, column=4, padx=5)
        
        # Фрейм для истории
        history_frame = ttk.LabelFrame(main_frame, text="История задач", padding="10")
        history_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        # Listbox для истории
        self.history_listbox = tk.Listbox(history_frame, height=12, width=60)
        self.history_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Scrollbar для listbox
        scrollbar = ttk.Scrollbar(history_frame, orient=tk.VERTICAL, 
                                 command=self.history_listbox.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.history_listbox.configure(yscrollcommand=scrollbar.set)
        
        # Кнопка очистки истории
        clear_btn = ttk.Button(history_frame, text="Очистить историю", 
                              command=self.clear_history)
        clear_btn.grid(row=1, column=0, pady=5)
        
        # Статус бар
        self.status_var = tk.StringVar(value="Готов к работе")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E))
        
        # Настройка grid для ресайза
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)
        history_frame.columnconfigure(0, weight=1)
        history_frame.rowconfigure(0, weight=1)
        
        # Отображение начальной истории
        self.update_history_display()
        
    def generate_task(self):
        """Генерация случайной задачи"""
        filter_type = self.filter_var.get()
        
        # Выбор задач в зависимости от фильтра
        if filter_type == "все":
            available_tasks = []
            for tasks in self.tasks.values():
                available_tasks.extend(tasks)
        else:
            available_tasks = self.tasks.get(filter_type, [])
        
        if not available_tasks:
            messagebox.showwarning("Предупреждение", "Нет доступных задач для выбранного типа")
            return
        
        # Выбор случайной задачи
        selected_task = random.choice(available_tasks)
        
        # Определение типа задачи
        task_type = self.get_task_type(selected_task)
        
        # Добавление в историю
        history_entry = {
            "task": selected_task,
            "type": task_type,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        self.history.append(history_entry)
        
        # Обновление отображения
        self.update_history_display()
        
        # Сохранение истории
        self.save_history()
        
        # Обновление статуса
        self.status_var.set(f"Сгенерирована задача: {selected_task}")
        
    def get_task_type(self, task):
        """Определение типа задачи"""
        for task_type, tasks in self.tasks.items():
            if task in tasks:
                return task_type
        return "неизвестно"
        
    def add_task(self):
        """Добавление новой задачи"""
        new_task = self.new_task_entry.get().strip()
        
        # Проверка на пустую строку
        if not new_task:
            messagebox.showerror("Ошибка", "Название задачи не может быть пустым!")
            return
        
        task_type = self.task_type_var.get()
        
        # Проверка на дубликат
        if new_task in self.tasks[task_type]:
            messagebox.showwarning("Предупреждение", "Такая задача уже существует!")
            return
        
        # Добавление задачи
        self.tasks[task_type].append(new_task)
        
        # Очистка поля ввода
        self.new_task_entry.delete(0, tk.END)
        
        # Обновление статуса
        self.status_var.set(f"Добавлена новая задача: {new_task} (тип: {task_type})")
        
        messagebox.showinfo("Успех", f"Задача '{new_task}' добавлена в категорию '{task_type}'")
        
    def update_history_display(self, event=None):
        """Обновление отображения истории"""
        self.history_listbox.delete(0, tk.END)
        
        filter_type = self.filter_var.get()
        
        # Фильтрация истории
        displayed_history = self.history
        if filter_type != "все":
            displayed_history = [entry for entry in self.history 
                               if entry["type"] == filter_type]
        
        # Отображение истории
        for entry in displayed_history[-50:]:  # Показываем последние 50 записей
            display_text = f"[{entry['timestamp']}] [{entry['type']}] {entry['task']}"
            self.history_listbox.insert(tk.END, display_text)
            
    def clear_history(self):
        """Очистка истории"""
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите очистить всю историю?"):
            self.history = []
            self.update_history_display()
            self.save_history()
            self.status_var.set("История очищена")
            
    def save_history(self):
        """Сохранение истории в JSON файл"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить историю: {str(e)}")
            
    def load_history(self):
        """Загрузка истории из JSON файла"""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    self.history = json.load(f)
        except Exception as e:
            messagebox.showwarning("Предупреждение", f"Не удалось загрузить историю: {str(e)}")
            self.history = []

def main():
    root = tk.Tk()
    app = RandomTaskGenerator(root)
    root.mainloop()

if __name__ == "__main__":
    main()
