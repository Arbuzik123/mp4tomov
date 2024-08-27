import os
import tkinter as tk
from tkinter import filedialog, messagebox
from ttkthemes import ThemedTk
from tkinter import ttk
from moviepy.editor import VideoFileClip
import threading
import sys


class TextRedirector:
    def __init__(self, widget):
        self.widget = widget

    def write(self, s):
        self.widget.configure(state="normal")
        self.widget.delete(1.0, tk.END)  # Очищаем содержимое виджета
        self.widget.insert(tk.END, s)
        self.widget.configure(state="disabled")
        self.widget.see("end")

    def flush(self):
        pass


def convert_video(input_path, output_path, log_widget):
    try:
        # Перенаправляем вывод логов в виджет
        sys.stdout = TextRedirector(log_widget)
        sys.stderr = TextRedirector(log_widget)  # также перенаправляем ошибки

        clip = VideoFileClip(input_path)
        clip.write_videofile(output_path, codec='libx264', verbose=True)

        print(
            f"Файл {os.path.basename(input_path)} успешно переконвертирован и сохранен как {os.path.basename(output_path)}")
    except Exception as e:
        print(f"Error: {e}")
        messagebox.showerror("Ошибка", f"Ошибка при конвертировании файла {os.path.basename(input_path)}")
    finally:
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__


def select_file():
    file_path = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4;*.wmv;*.avi;*.m2ts;*.mkv")])
    if file_path:
        input_path.set(file_path)
        messagebox.showinfo("Файл выбран", f"Выбран файл: {file_path}")


def save_file():
    output_path = filedialog.asksaveasfilename(defaultextension=".mov", filetypes=[
        ("MOV files", "*.mov"),
        ("WMV files", "*.wmv"),
        ("AVI files", "*.avi"),
        ("MKV files", "*.mkv"),
        ("AVCHD files", "*.m2ts"),
    ])
    if output_path and input_path.get():
        log_widget.configure(state="normal")
        log_widget.delete(1.0, "end")
        log_widget.configure(state="disabled")
        conversion_thread = threading.Thread(target=convert_video, args=(input_path.get(), output_path, log_widget))
        conversion_thread.start()
    elif not input_path.get():
        messagebox.showerror("Ошибка", "Сначала выберите файл")
    elif not output_path:
        messagebox.showerror("Ошибка", "Выберите путь сохранения")


def select_folder():
    folder_path = filedialog.askdirectory()
    if folder_path:
        input_folder.set(folder_path)
        messagebox.showinfo("Папка выбрана", f"Выбрана папка: {folder_path}")


def save_folder():
    folder_path = filedialog.askdirectory()
    if folder_path:
        output_folder.set(folder_path)
        messagebox.showinfo("Папка для сохранения выбрана", f"Сохранение в: {folder_path}")
        log_widget.configure(state="normal")
        log_widget.delete(1.0, "end")
        log_widget.configure(state="disabled")
        conversion_thread = threading.Thread(target=process_videos,
                                             args=(input_folder.get(), output_folder.get(), log_widget))
        conversion_thread.start()
    else:
        messagebox.showerror("Ошибка", "Выберите папку для сохранения")


def process_videos(input_folder, output_folder, log_widget):
    # Получаем список всех файлов в выбранной папке
    video_files = [f for f in os.listdir(input_folder) if f.endswith(('.mp4', '.wmv', '.avi', '.m2ts', '.mkv'))]

    if not video_files:
        messagebox.showerror("Ошибка", "В выбранной папке нет видеофайлов для конвертации")
        return

    for video_file in video_files:
        input_path = os.path.join(input_folder, video_file)
        output_path = os.path.join(output_folder, os.path.splitext(video_file)[0] + ".mov")
        convert_video(input_path, output_path, log_widget)

    messagebox.showinfo("Успешно", "Все файлы успешно переконвертированы!")


# Создаем основное окно приложения с темой
root = ThemedTk(theme="arc")
root.title("Video Converter")
root.iconbitmap("free-icon-convert-4700974.ico")

# Устанавливаем размер окна
root.geometry("600x500")

# Переменные для хранения путей
input_path = tk.StringVar()
input_folder = tk.StringVar()
output_folder = tk.StringVar()

# Размещаем кнопки одна над другой
select_button = ttk.Button(root, text="Выбрать видеофайл", command=select_file)
select_button.pack(fill="x", padx=20, pady=10)

save_button = ttk.Button(root, text="Сохранить как", command=save_file)
save_button.pack(fill="x", padx=20, pady=10)

# Новые кнопки для выбора и сохранения папок
select_folder_button = ttk.Button(root, text="Выбрать папку с видеофайлами", command=select_folder)
select_folder_button.pack(fill="x", padx=20, pady=10)

save_folder_button = ttk.Button(root, text="Выбрать папку для сохранения", command=save_folder)
save_folder_button.pack(fill="x", padx=20, pady=10)

# Виджет для вывода логов
log_widget = tk.Text(root, height=10, state="disabled")
log_widget.pack(fill="both", padx=20, pady=20, expand=True)

# Запуск главного цикла приложения
root.mainloop()
