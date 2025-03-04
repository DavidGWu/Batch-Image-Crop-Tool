import os
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

class ImageCropTool:
    def __init__(self, master):
        self.master = master
        self.master.title("Batch Image Crop Tool")
        self.master.geometry("800x800")

        self.image_folder = ""
        self.output_folder = ""
        self.image_files = []
        self.current_index = 0

        self.crop_size_x = 0
        self.crop_size_y = 0

        # Create menu bar
        self.menu_bar = tk.Menu(master)
        master.config(menu=self.menu_bar)
        # Add File menu
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)

        self.file_menu.add_command(label="Open Folder", command=self.set_input_folder)
        self.file_menu.add_command(label="Save Folder", command=self.set_output_folder)
        # Add Edit menu
        self.edit_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Edit", menu=self.edit_menu)

        self.auto_crop_enabled = tk.BooleanVar(value=True)
        self.edit_menu.add_checkbutton(label="Enable Auto Start Crop", variable=self.auto_crop_enabled)

        self.display_after_crop = tk.BooleanVar(value=True)
        self.edit_menu.add_checkbutton(label="Display after crop", variable=self.display_after_crop)

        # Add Help menu
        self.help_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Help", menu=self.help_menu)

        self.help_menu.add_command(label="About", command=self.show_about)



        # Top toolbar
        self.top_toolbar = tk.Frame(master)
        self.top_toolbar.pack(side=tk.TOP, fill=tk.X)

        rotate_left_icon = Image.open(os.path.join("icons", "rotate-left.png"))
        rotate_left_icon = rotate_left_icon.resize((20, 20), Image.LANCZOS)
        rotate_left_icon = ImageTk.PhotoImage(rotate_left_icon)
        self.rotate_left_button = tk.Button(self.top_toolbar, image=rotate_left_icon, command=self.rotate_left)
        self.rotate_left_button.image = rotate_left_icon
        self.rotate_left_button.pack(side=tk.LEFT, padx=5, pady=10)

        rotate_right_icon = Image.open(os.path.join("icons", "rotate-right.png"))
        rotate_right_icon = rotate_right_icon.resize((20, 20), Image.LANCZOS)
        rotate_right_icon = ImageTk.PhotoImage(rotate_right_icon)
        self.rotate_right_button = tk.Button(self.top_toolbar, image=rotate_right_icon, command=self.rotate_right)
        self.rotate_right_button.image = rotate_right_icon
        self.rotate_right_button.pack(side=tk.LEFT, padx=5, pady=10)

        self.next_button = tk.Button(self.top_toolbar, text="Next-->", command=self.next_image)
        self.next_button.pack(side=tk.RIGHT, padx=5, pady=10)
        self.prev_button = tk.Button(self.top_toolbar, text="<--Prev", command=self.prev_image)
        self.prev_button.pack(side=tk.RIGHT, padx=5, pady=10)

        self.crop_button = tk.Button(self.top_toolbar, text="Crop", command=self.crop_image)
        self.crop_button.pack(side=tk.LEFT, padx=5, pady=10)

        tk.Label(self.top_toolbar, text="Crop Size:").pack(side=tk.LEFT, padx=5, pady=5)
        self.size_entry = tk.Entry(self.top_toolbar)
        self.size_entry.insert(0, "512x512")
        self.size_entry.pack(side=tk.LEFT, padx=5, pady=5)

        self.message_label = tk.Label(self.top_toolbar, text="", fg="green")
        self.message_label.pack(pady=10)

        self.canvas = tk.Canvas(master, bg='gray')
        self.canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.thumbnail_frame = tk.Frame(master, width=self.master.winfo_width())
        self.thumbnail_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.thumbnail_canvas = tk.Canvas(self.thumbnail_frame, height=100, bg='white')
        self.thumbnail_canvas.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.thumbnail_inner_frame = tk.Frame(self.thumbnail_canvas)
        self.thumbnail_canvas.create_window((0, 0), window=self.thumbnail_inner_frame, anchor='nw')

        self.canvas.bind("<Configure>", self.resize_image)

        self.rect = None
        self.start_x = None
        self.start_y = None

    def set_input_folder(self):
        self.image_folder = filedialog.askdirectory(title="Select Image Folder")
        self.image_files = [f for f in os.listdir(self.image_folder) if f.lower().endswith(('png', 'jpg', 'jpeg', 'bmp'))]
        self.current_index = 0
        if self.image_files:
            self.load_image()
            self.load_thumbnails()

    def set_output_folder(self):
        self.output_folder = filedialog.askdirectory(title="Select Output Folder")

    def load_image(self):
        image_path = os.path.join(self.image_folder, self.image_files[self.current_index])
        self.original_image = Image.open(image_path)
        self.display_image()
        if self.auto_crop_enabled.get():
            self.canvas.bind("<ButtonPress-1>", self.start_crop)
            self.canvas.bind("<B1-Motion>", self.draw_crop_rect)
            self.canvas.bind("<ButtonRelease-1>", self.finish_crop)
            try:
                self.crop_size_x, self.crop_size_y = map(int, self.size_entry.get().split('x'))
            except ValueError:
                messagebox.showerror("Error", "Invalid crop size format. Use (Width)x(Height) format. E,g, 512x512.")
                return

    def display_image(self):
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        if hasattr(self, 'original_image'):
            self.resized_image = self.original_image.copy()
        else:
            return
        self.resized_image.thumbnail((canvas_width, canvas_height), Image.LANCZOS)
        self.tk_image = ImageTk.PhotoImage(self.resized_image)
        self.canvas.delete("all")
        self.canvas.create_image(canvas_width//2, canvas_height//2, image=self.tk_image, anchor=tk.CENTER)

    def resize_image(self, event):
        self.display_image()

    def crop_image(self):
        crop_size_text = self.size_entry.get()
        try:
            self.crop_size_x, self.crop_size_y = map(int, crop_size_text.split('x'))
        except ValueError:
            messagebox.showerror("Error", "Invalid crop size format. Use MxN format.")
            return
        self.canvas.bind("<ButtonPress-1>", self.start_crop)
        self.canvas.bind("<B1-Motion>", self.draw_crop_rect)
        self.canvas.bind("<ButtonRelease-1>", self.finish_crop)

    def start_crop(self, event):
        self.canvas.delete("crop_rect")
        self.start_x, self.start_y = event.x, event.y
        self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline='red', tag="crop_rect")

    def draw_crop_rect(self, event):
        end_x, end_y = event.x, event.y
        width = abs(end_x - self.start_x)
        height = abs(end_y - self.start_y)

        if width == 0 or height == 0:
            return
        aspect_ratio = self.crop_size_x / self.crop_size_y

        if width / height > aspect_ratio:
            width = height * aspect_ratio
        else:
            height = width / aspect_ratio

        if end_x < self.start_x:
            end_x = self.start_x - width
        else:
            end_x = self.start_x + width

        if end_y < self.start_y:
            end_y = self.start_y - height
        else:
            end_y = self.start_y + height

        self.canvas.coords(self.rect, self.start_x, self.start_y, end_x, end_y)

    def finish_crop(self, event):
        bbox = self.canvas.coords(self.rect)
        scale_x = self.original_image.width / self.resized_image.width
        scale_y = self.original_image.height / self.resized_image.height

        x1 = int(min(bbox[0], bbox[2]) - (self.canvas.winfo_width() - self.resized_image.width)//2)
        y1 = int(min(bbox[1], bbox[3]) - (self.canvas.winfo_height() - self.resized_image.height)//2)
        x2 = int(max(bbox[0], bbox[2]) - (self.canvas.winfo_width() - self.resized_image.width)//2)
        y2 = int(max(bbox[1], bbox[3]) - (self.canvas.winfo_height() - self.resized_image.height)//2)

        x1, y1, x2, y2 = [int(coord * scale_x) for coord in [x1, y1, x2, y2]]

        cropped = self.original_image.crop((x1, y1, x2, y2)).resize((self.crop_size_x, self.crop_size_y), Image.LANCZOS)
        if self.display_after_crop.get():
            cropped.show()

        if not self.output_folder:
            messagebox.showwarning("Warning", "Please set the output folder before cropping.")
            return

        output_path = os.path.join(self.output_folder, self.image_files[self.current_index])
        cropped.save(output_path)

        self.message_label.config(text="Crop finished!")

        if not self.auto_crop_enabled.get():
            self.canvas.unbind("<ButtonPress-1>")
            self.canvas.unbind("<B1-Motion>")
            self.canvas.unbind("<ButtonRelease-1>")

    def prev_image(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.load_image()
            self.highlight_thumbnail()
            self.scroll_to_thumbnail()
            if not self.auto_crop_enabled.get():
                self.canvas.unbind("<ButtonPress-1>")
                self.canvas.unbind("<B1-Motion>")
                self.canvas.unbind("<ButtonRelease-1>")
            else:
                self.canvas.bind("<ButtonPress-1>", self.start_crop)
                self.canvas.bind("<B1-Motion>", self.draw_crop_rect)
                self.canvas.bind("<ButtonRelease-1>", self.finish_crop)
            self.message_label.config(text="")
        else:
            messagebox.showinfo("Info", "This is the first image.")
        if hasattr(self, 'original_image'):
            self.original_image = self.original_image
        else:
            self.original_image = None

    def next_image(self):
        self.current_index += 1
        if self.current_index >= len(self.image_files):
            messagebox.showinfo("Done", "No more images.")
        else:
            self.load_image()
            self.highlight_thumbnail()
            self.scroll_to_thumbnail()

            if not self.auto_crop_enabled.get():
                self.canvas.unbind("<ButtonPress-1>")
                self.canvas.unbind("<B1-Motion>")
                self.canvas.unbind("<ButtonRelease-1>")
            else:
                self.canvas.bind("<ButtonPress-1>", self.start_crop)
                self.canvas.bind("<B1-Motion>", self.draw_crop_rect)
                self.canvas.bind("<ButtonRelease-1>", self.finish_crop)
            self.message_label.config(text="")

    def load_thumbnails(self):
        for widget in self.thumbnail_inner_frame.winfo_children():
            widget.destroy()

        for index, image_file in enumerate(self.image_files):
            image_path = os.path.join(self.image_folder, image_file)
            image = Image.open(image_path)
            image.thumbnail((100, 100), Image.LANCZOS)
            tk_image = ImageTk.PhotoImage(image)

            label = tk.Label(self.thumbnail_inner_frame, image=tk_image, borderwidth=2, relief="solid")
            label.image = tk_image
            label.grid(row=0, column=index, padx=5, pady=5)
            label.bind("<Button-1>", lambda e, idx=index: self.load_image_from_thumbnail(idx))

        self.thumbnail_inner_frame.update_idletasks()
        self.thumbnail_canvas.config(scrollregion=self.thumbnail_canvas.bbox("all"))

    def load_image_from_thumbnail(self, index):
        self.current_index = index
        self.load_image()
        self.highlight_thumbnail()
        self.scroll_to_thumbnail()
        if not self.auto_crop_enabled.get():
            self.canvas.unbind("<ButtonPress-1>")
            self.canvas.unbind("<B1-Motion>")
            self.canvas.unbind("<ButtonRelease-1>")
        else:
            self.canvas.bind("<ButtonPress-1>", self.start_crop)
            self.canvas.bind("<B1-Motion>", self.draw_crop_rect)
            self.canvas.bind("<ButtonRelease-1>", self.finish_crop)

    def highlight_thumbnail(self):
        for widget in self.thumbnail_inner_frame.winfo_children():
            widget.config(borderwidth=2, relief="solid")
        self.thumbnail_inner_frame.winfo_children()[self.current_index].config(borderwidth=2, relief="raised", bg="red")

    def scroll_to_thumbnail(self):
        thumbnail_width = 110  # Assuming each thumbnail is 100x100 with 5px padding on each side
        canvas_width = self.thumbnail_canvas.winfo_width()
        middle_index = canvas_width // (2 * thumbnail_width)
        scroll_position = max(0, (self.current_index - middle_index) * thumbnail_width)
        self.thumbnail_canvas.xview_moveto(scroll_position / self.thumbnail_canvas.bbox("all")[2])

    def rotate_left(self):
        self.original_image = self.original_image.rotate(90, expand=True)
        self.save_and_reload_image()
        self.load_thumbnails()

    def rotate_right(self):
        self.original_image = self.original_image.rotate(-90, expand=True)
        self.save_and_reload_image()
        self.load_thumbnails()

    def save_and_reload_image(self):
        image_path = os.path.join(self.image_folder, self.image_files[self.current_index])
        self.original_image.save(image_path)
        self.load_image()
        self.highlight_thumbnail()
    def show_about(self):
        messagebox.showinfo("About", "Author: Guangzheng Wu \n GitHub: https://github.com/yourusername")
        
if __name__ == "__main__":
    root = tk.Tk()
    app = ImageCropTool(root)
    root.mainloop()