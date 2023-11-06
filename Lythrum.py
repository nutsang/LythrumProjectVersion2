import os
import customtkinter
import CTkMessagebox
import CTkToolTip
import Lythrum_extensions
import functools
import threading
import random
import time
import subprocess
import concurrent.futures

global list_process
global list_success
global choose_format_all_window
list_process = []
list_success = []
choose_format_all_window = None

# Setting
title_name = 'Lythrum'

asset_folder = os.path.join(os.getcwd(), 'asset')

icon_file = os.path.join(asset_folder, 'icon.ico')

custom_font_file = os.path.join(asset_folder, 'Itim-Regular.ttf')
customtkinter.FontManager.load_font(custom_font_file)
font_name = 'Itim'

custom_theme_file = os.path.join(asset_folder, 'custom_theme.json')
customtkinter.set_default_color_theme(custom_theme_file)

display_width = 1420
display_height = 600

class Process():
    def __init__(self, source_file):
        self.priority = 0
        self.file_status = 'พร้อม'
        self.source_file = source_file
        self.file_size = os.path.getsize(source_file)
        self.file_basename = os.path.basename(source_file)
        self.file_name, self.file_extension = os.path.splitext(self.file_basename)
        self.display_file_name = set_display_file_name(self.file_name, self.file_extension)
        self.display_file_size = set_display_file_size(self.file_size)

    def set_priority(self, priority):
        self.priority = priority
        
    def set_file_status(self, file_status):
        self.file_status = file_status
        
    def set_process_frame(self, process_frame):
        self.process_frame = process_frame
        
    def set_folder_destination(self, folder_destination):
        self.folder_destination = folder_destination
        
    def set_destination_extension(self, destination_extension):
        self.destination_extension = destination_extension

    def set_show_file_progress_widget(self, show_file_progress_widget):
        self.show_file_progress_widget = show_file_progress_widget
        
    def set_display_file_name_widget(self, display_file_name_widget):
        self.display_file_name_widget = display_file_name_widget
        
    def set_display_file_size_widget(self, display_file_size_widget):
        self.display_file_size_widget = display_file_size_widget
        
    def set_display_file_status_widget(self, display_file_status_widget):
        self.display_file_status_widget = display_file_status_widget
        
    def set_combobox_choose_format(self, combobox_choose_format):
        self.combobox_choose_format = combobox_choose_format
        
    def set_btn_delete_file_widget(self, btn_delete_file_widget):
        self.btn_delete_file_widget = btn_delete_file_widget
        
def set_display_file_name(file_name, file_extension):
    maximum_length_file_name = 11
    display_file_name = f'{file_name}{file_extension}'
    if(len(file_name) > maximum_length_file_name):
        display_file_name = f'{file_name[0:maximum_length_file_name]}... {file_extension}'
    return display_file_name

def set_display_file_size(file_size):
    unit = 'Byte'
    if file_size >= 1099511627776:
        file_size /=  1099511627776
        unit = 'TB'
    elif file_size >= 1073741824:
        file_size /= 1073741824
        unit = 'GB'
    elif file_size >= 1048576:
        file_size /= 1048576
        unit = 'MB'
    elif file_size >= 1024:
        file_size /= 1024
        unit = 'KB'
    display_file_size = f'{file_size:.2f} {unit}'
    return display_file_size

def shortest_job_first(process):
    return sorted(process, key = lambda process : process.file_size)

def delete_file(process):
    if(process.file_status in {'พร้อม', 'เสร็จสิ้น', 'ผิดพลาด'}):
        process.process_frame.destroy()
        if process in list_process:
            list_process.remove(process)
        if process in list_success:
            list_success.remove(process)
        del process
        btn_show_unsuccess.configure(text= f'จำนวนไฟล์: {len(list_process)}')
        btn_show_success.configure(text= f'เสร็จสิ้น: {len(list_success)}')
 
def clear_all_unsuccess():
    confirm = 'ใช่, ฉันต้องการ'
    message = CTkMessagebox.CTkMessagebox(title='ยืนยัน', message='คุณต้องการจะล้างไฟล์ทั้งหมด', icon='question', option_1=confirm, option_2='ไม่, ยกเลิก', fade_in_duration=0.2, font=font_theme_16)
    if message.get() == confirm:
        global list_process
        temp_list_process = list_process.copy()
        for process in temp_list_process:
            if process.display_file_status_widget.cget('text') in {'พร้อม', 'เสร็จสิ้น:', 'ผิดพลาด'}:
                list_process.remove(process)
                process.process_frame.destroy()
                del process
        btn_show_unsuccess.configure(text=f'จำนวนไฟล์: {len(list_process)}')

def clear_all_success():
    confirm = 'ใช่, ฉันต้องการ'
    message = CTkMessagebox.CTkMessagebox(title='ยืนยัน', message='คุณต้องการจะล้างไฟล์ทั้งหมด', icon='question', option_1=confirm, option_2='ไม่, ยกเลิก', fade_in_duration=0.2, font=font_theme_16)
    if message.get() == confirm:
        global list_success
        temp_list_success = list_success.copy()
        for process in temp_list_success:
            list_success.remove(process)
            process.process_frame.destroy()
            del process
        btn_show_success.configure(text=f'เสร็จสิ้น: {len(list_success)}')
    
def browse_files_source():
    btn_choose_files.configure(text='กำลังนำเข้า...', state='disabled')
    file_paths = customtkinter.filedialog.askopenfilenames(title='นำเข้าไฟล์ที่ต้องการแปลง', filetypes=[('ไฟล์ทั้งหมด', '*.*')])
    if file_paths:
        if(len(list_process) + len(file_paths) > 100):
            CTkMessagebox.CTkMessagebox(title='คำเตือน', message='รองรับไฟล์ได้สูงสุด 100 ไฟล์',icon='warning', option_1='ตกลง', font=font_theme_16, sound='enabled')
        else:
            for source_file in file_paths:
                process = Process(source_file.replace("\\","/"))
                list_process.append(process)
            index_start_frame = len(list_process)-len(file_paths)
            combobox_format_options = Lythrum_extensions.list_extensions.copy()
            combobox_format_options.insert(0, '...')
            
            for row, process in enumerate(list_process[index_start_frame:], start=index_start_frame):
                process_frame = customtkinter.CTkFrame(master=sf_show_unsuccess)
                process_frame.columnconfigure(0, weight=2)
                process_frame.columnconfigure(1, weight=1)
                process_frame.columnconfigure(2, weight=1)
                process_frame.columnconfigure(3, weight=1)
                process_frame.columnconfigure(4, weight=1)
                process_frame.rowconfigure(0, weight=1)
                show_file_progress_widget = customtkinter.CTkProgressBar(master=process_frame, mode='indeterminate', orientation='horizontal')
                display_file_name_widget = customtkinter.CTkLabel(master=process_frame, text=process.display_file_name, font=font_theme_18)
                display_file_size_widget = customtkinter.CTkLabel(master=process_frame, text=process.display_file_size, font=font_theme_18)
                CTkToolTip.CTkToolTip(display_file_name_widget, delay=0.5, message=process.file_basename)
                display_file_status_widget = customtkinter.CTkButton(master=process_frame, text=process.file_status, font=font_theme_18)
                combobox_format_variable = customtkinter.StringVar(value=combobox_format_options[0])
                combobox_choose_format = customtkinter.CTkOptionMenu(values=combobox_format_options, variable=combobox_format_variable, dynamic_resizing='enable', master=process_frame, font=font_theme_18, dropdown_font=font_theme_18)
                delete_file_partial = functools.partial(delete_file, process)
                btn_delete_file_widget = customtkinter.CTkButton(command=delete_file_partial, master=process_frame, text='ลบ', font=font_theme_18)
                display_file_name_widget.grid(row=0, column=0, padx=10, pady=10, sticky='news')
                display_file_size_widget.grid(row=0, column=1, padx=10, pady=10, sticky='news')
                display_file_status_widget.grid(row=0, column=2, padx=10, pady=10, sticky='news')
                combobox_choose_format.grid(row=0, column=3, padx=10, pady=10, sticky='news')
                btn_delete_file_widget.grid(row=0, column=4, padx=10, pady=10, sticky='news')
                process.set_process_frame(process_frame)
                process_frame.grid(row=row, column=0, columnspan=3, padx=10, pady=10, sticky='news')
                process.set_show_file_progress_widget(show_file_progress_widget)
                process.set_display_file_name_widget(display_file_name_widget)
                process.set_display_file_size_widget(display_file_size_widget)
                process.set_display_file_status_widget(display_file_status_widget)
                process.set_combobox_choose_format(combobox_choose_format)
                process.set_btn_delete_file_widget(btn_delete_file_widget)
                btn_show_unsuccess.configure(text= f'จำนวนไฟล์: {len(list_process)}')
        btn_choose_files.configure(text='นำเข้า', state='normal')
        
def browse_folder_destination():
    btn_choose_folder.configure(text='กำลังเลือกปลายทาง...', state='disabled')
    folder_path = customtkinter.filedialog.askdirectory()
    if folder_path:
        folder_destination.set(os.path.join(folder_path,'OUTPUT').replace("\\","/"))
        tooltip_choose_folder.configure(message=folder_destination.get())
    btn_choose_folder.configure(text='ปลายทาง', state='normal')

def choose_format(format_name):
    global list_process
    for process in list_process:
        if process.display_file_status_widget.cget('text') == 'พร้อม':
            process.combobox_choose_format.set(format_name)

def choose_format_all():
    global choose_format_all_window
    if choose_format_all_window is None or not choose_format_all_window.winfo_exists():
        choose_format_all_window = customtkinter.CTkToplevel(master=lythrum)
        choose_format_all_window.title('เลือกรูปแบบไฟล์ทั้งหมด')
        choose_format_all_window.columnconfigure(0, weight=1)
        choose_format_all_window.columnconfigure(1, weight=1)
        video_extensions = Lythrum_extensions.video_extensions.copy()
        audio_extensions = Lythrum_extensions.audio_extensions.copy()
        for row, format_name in enumerate(video_extensions):
            choose_format_partial = functools.partial(choose_format, format_name)
            btn_format_name = customtkinter.CTkButton(command=choose_format_partial, master=choose_format_all_window, text=format_name, font=font_theme_24)
            btn_format_name.grid(row=row, column=0, padx=10, pady=10, sticky='news')
            choose_format_all_window.rowconfigure(row, weight=1)
        for row, format_name in enumerate(audio_extensions):
            choose_format_partial = functools.partial(choose_format, format_name)
            btn_format_name = customtkinter.CTkButton(command=choose_format_partial, master=choose_format_all_window, text=format_name, font=font_theme_24)
            btn_format_name.grid(row=row, column=1, padx=10, pady=10, sticky='news')
            choose_format_all_window.rowconfigure(row, weight=1)
    else:
        choose_format_all_window.focus()

def auto_select_gpu(ffmpeg, process, video_codec='libx264', audio_codec='libmp3lame', gpu=0):
    file_destination = os.path.join(process.folder_destination, f'{process.file_name}{process.destination_extension}').replace('\\','/')
    if os.path.isfile(file_destination):
        os.remove(file_destination)
    if process.destination_extension in Lythrum_extensions.audio_extensions_set:
        if process.destination_extension == '.wav':
            audio_codec = 'pcm_s16le'
        elif process.destination_extension == '.aac':
            audio_codec = 'aac'
        ffmpeg_cmd = f'"{ffmpeg}" -i "{process.source_file}" -vn -acodec {audio_codec} "{file_destination}"'
        gpu=3
    else:
        if process.destination_extension in Lythrum_extensions.video_extensions_set:
            video_codec_gpu = ''
            if gpu < 3:
                video_codec = 'h264'
            if gpu == 0:
                video_codec_gpu = '_nvenc'
            elif gpu == 1:
                video_codec_gpu = '_amf'
            elif gpu == 2:
                video_codec_gpu = '_qsv'
            ffmpeg_cmd = f'"{ffmpeg}" -i "{process.source_file}" -vcodec {video_codec}{video_codec_gpu} -acodec {audio_codec} "{file_destination}"'
        else:
            if process.destination_extension == '.mov':
                audio_codec='aac'
            ffmpeg_cmd = f'"{ffmpeg}" -i "{process.source_file}" -vcodec {video_codec} -acodec {audio_codec} "{file_destination}"'
            gpu=3
    if gpu > 2:
        try:
            subprocess.run(ffmpeg_cmd.replace('\\','/'), shell=True, check=True)
            process.set_file_status('เสร็จสิ้น')
            process.display_file_status_widget.configure(text='เสร็จสิ้น')
            return process
        except:
            if os.path.isfile(file_destination):
                os.remove(file_destination)
            process.set_file_status('ผิดพลาด')
            process.display_file_status_widget.configure(text='ผิดพลาด')
            return process
    else:
        try:
            subprocess.run(ffmpeg_cmd.replace('\\','/'), shell=True, check=True)
            process.set_file_status('เสร็จสิ้น')
            process.display_file_status_widget.configure(text='เสร็จสิ้น')
            return process
        except:
            return auto_select_gpu(ffmpeg, process, gpu=gpu+1)

def convert_file(process):
    process.display_file_status_widget.configure(text='ดำเนินการ...')
    process.set_file_status('ดำเนินการ...')
    process.show_file_progress_widget.grid(row=0, column=3, padx=10, pady=10, sticky='news')
    process.show_file_progress_widget.start()
    ffmpeg = os.path.join(asset_folder, 'ffmpeg', 'bin', 'ffmpeg.exe')
    return auto_select_gpu(ffmpeg, process)

def convert():
    if(folder_destination.get() == ''):
        CTkMessagebox.CTkMessagebox(title='คำเตือน', message='กรุณาระบุโฟลเดอร์ปลายทาง',icon='warning', option_1='ตกลง', font=font_theme_16, sound='enabled')
    else:
        if not os.path.exists(folder_destination.get()):
            os.makedirs(folder_destination.get())
        global list_process
        global list_success
        queue_process = []
        process_video = []
        process_audio = []
        for process in list_process.copy():
            if process.combobox_choose_format.get() != '...' and process.display_file_status_widget.cget('text') == 'พร้อม':
                process.combobox_choose_format.grid_forget()
                process.btn_delete_file_widget.grid_forget()
                process.display_file_status_widget.configure(text='รอดำเนินการ...')
                process.set_file_status('รอดำเนินการ...')
                if process.file_extension in Lythrum_extensions.set_extensions:
                    process.set_destination_extension(process.combobox_choose_format.get().lower())
                    process.set_folder_destination(folder_destination.get().replace('\\','/'))
                    if process.destination_extension in Lythrum_extensions.video_extensions_set:
                        process.set_priority(1)
                        process_video.append(process)
                    elif process.destination_extension in Lythrum_extensions.audio_extensions_set:
                        process.set_priority(0)
                        process_audio.append(process)
                else:
                    process.display_file_status_widget.configure(text='ผิดพลาด')
                    process.set_file_status('ผิดพลาด')
                    process_success = Process(process.source_file)
                    list_success.append(process_success)
                    index_start_frame = len(list_success)-1
                    combobox_format_options = Lythrum_extensions.list_extensions.copy()
                    combobox_format_options.insert(0, '...')
                    process_frame = customtkinter.CTkFrame(master=sf_show_success)
                    process_frame.columnconfigure(0, weight=2)
                    process_frame.columnconfigure(1, weight=1)
                    process_frame.columnconfigure(2, weight=1)
                    process_frame.columnconfigure(3, weight=1)
                    process_frame.columnconfigure(4, weight=1)
                    process_frame.rowconfigure(0, weight=1)
                    show_file_progress_widget = customtkinter.CTkProgressBar(master=process_frame, mode='indeterminate', orientation='horizontal')
                    display_file_name_widget = customtkinter.CTkLabel(master=process_frame, text=process.display_file_name, font=font_theme_18)
                    display_file_size_widget = customtkinter.CTkLabel(master=process_frame, text=process.display_file_size, font=font_theme_18)
                    CTkToolTip.CTkToolTip(display_file_name_widget, delay=0.01, message=process_success.file_basename)
                    display_file_status_widget = customtkinter.CTkButton(master=process_frame, text=process_success.file_status, font=font_theme_18)
                    combobox_format_variable = customtkinter.StringVar(value=combobox_format_options[0])
                    combobox_choose_format = customtkinter.CTkOptionMenu(values=combobox_format_options, variable=combobox_format_variable, dynamic_resizing='enable', master=process_frame, font=font_theme_18, dropdown_font=font_theme_18)
                    delete_file_partial = functools.partial(delete_file, process_success)
                    btn_delete_file_widget = customtkinter.CTkButton(command=delete_file_partial, master=process_frame, text='ลบ', font=font_theme_18)
                    display_file_name_widget.grid(row=0, column=0, padx=10, pady=10, sticky='news')
                    display_file_size_widget.grid(row=0, column=1, padx=10, pady=10, sticky='news')
                    display_file_status_widget.grid(row=0, column=2, padx=10, pady=10, sticky='news')
                    combobox_choose_format.grid(row=0, column=3, padx=10, pady=10, sticky='news')
                    btn_delete_file_widget.grid(row=0, column=4, padx=10, pady=10, sticky='news')
                    process_success.set_process_frame(process_frame)
                    process_frame.grid(row=len(sf_show_success.winfo_children()), column=0, columnspan=3, padx=10, pady=10, sticky='news')
                    process_success.set_show_file_progress_widget(show_file_progress_widget)
                    process_success.set_display_file_name_widget(display_file_name_widget)
                    process_success.set_display_file_size_widget(display_file_size_widget)
                    process_success.set_display_file_status_widget(display_file_status_widget)
                    process_success.set_combobox_choose_format(combobox_choose_format)
                    process_success.set_btn_delete_file_widget(btn_delete_file_widget)
                    process_success.combobox_choose_format.grid_forget()
                    process_success.display_file_status_widget.configure(text='ผิดพลาด')
                    process_success.set_file_status('ผิดพลาด')
                    if process.file_status == 'ผิดพลาด':
                        process.process_frame.destroy()
                        if process in list_process:
                            list_process.remove(process)
                            del process
                    btn_show_unsuccess.configure(text= f'จำนวนไฟล์: {len(list_process)}')
                    btn_show_success.configure(text= f'เสร็จสิ้น: {len(list_success)}')
        queue_process.extend(shortest_job_first(process_audio))
        queue_process.extend(shortest_job_first(process_video))
        process_amount = len(queue_process)
        if process_amount > 0:
            list_fininshed = []
            process_step = (((1 / process_amount) * 100) / 100) * 50
            btn_convert.configure(text='กำลังแปลง...', state='disabled')
            process_progress.configure(determinate_speed=process_step)
            process_progress.set(0)
            workers = process_amount if process_amount < 5 else 4
            with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
                futures = [executor.submit(convert_file, p) for p in queue_process]
                for future in concurrent.futures.as_completed(futures):
                    process_progress.step()
                    if future.done():
                        process = future.result()
                        process.process_frame.grid_forget()
                        process_success = Process(process.source_file)
                        list_fininshed.append(process)
                        list_success.append(process_success)
                        index_start_frame = len(list_success)-1
                        combobox_format_options = Lythrum_extensions.list_extensions.copy()
                        combobox_format_options.insert(0, '...')
                        process_frame = customtkinter.CTkFrame(master=sf_show_success)
                        process_frame.columnconfigure(0, weight=2)
                        process_frame.columnconfigure(1, weight=1)
                        process_frame.columnconfigure(2, weight=1)
                        process_frame.columnconfigure(3, weight=1)
                        process_frame.columnconfigure(4, weight=1)
                        process_frame.rowconfigure(0, weight=1)
                        show_file_progress_widget = customtkinter.CTkProgressBar(master=process_frame, mode='indeterminate', orientation='horizontal')
                        display_file_name_widget = customtkinter.CTkLabel(master=process_frame, text=process.display_file_name, font=font_theme_18)
                        display_file_size_widget = customtkinter.CTkLabel(master=process_frame, text=process.display_file_size, font=font_theme_18)
                        CTkToolTip.CTkToolTip(display_file_name_widget, delay=0.01, message=process_success.file_basename)
                        display_file_status_widget = customtkinter.CTkButton(master=process_frame, text=process_success.file_status, font=font_theme_18)
                        combobox_format_variable = customtkinter.StringVar(value=combobox_format_options[0])
                        combobox_choose_format = customtkinter.CTkOptionMenu(values=combobox_format_options, variable=combobox_format_variable, dynamic_resizing='enable', master=process_frame, font=font_theme_18, dropdown_font=font_theme_18)
                        delete_file_partial = functools.partial(delete_file, process_success)
                        btn_delete_file_widget = customtkinter.CTkButton(command=delete_file_partial, master=process_frame, text='ลบ', font=font_theme_18)
                        display_file_name_widget.grid(row=0, column=0, padx=10, pady=10, sticky='news')
                        display_file_size_widget.grid(row=0, column=1, padx=10, pady=10, sticky='news')
                        display_file_status_widget.grid(row=0, column=2, padx=10, pady=10, sticky='news')
                        combobox_choose_format.grid(row=0, column=3, padx=10, pady=10, sticky='news')
                        btn_delete_file_widget.grid(row=0, column=4, padx=10, pady=10, sticky='news')
                        process_success.set_process_frame(process_frame)
                        process_frame.grid(row=len(sf_show_success.winfo_children()), column=0, columnspan=3, padx=10, pady=10, sticky='news')
                        process_success.set_show_file_progress_widget(show_file_progress_widget)
                        process_success.set_display_file_name_widget(display_file_name_widget)
                        process_success.set_display_file_size_widget(display_file_size_widget)
                        process_success.set_display_file_status_widget(display_file_status_widget)
                        process_success.set_combobox_choose_format(combobox_choose_format)
                        process_success.set_btn_delete_file_widget(btn_delete_file_widget)
                        process_success.combobox_choose_format.grid_forget()
                        process_success.display_file_status_widget.configure(text=process.display_file_status_widget.cget('text'))
                        process_success.set_file_status(process.file_status)
                        list_process.remove(process)
                        btn_show_unsuccess.configure(text= f'จำนวนไฟล์: {len(list_process)}')
                        btn_show_success.configure(text= f'เสร็จสิ้น: {len(list_success)}')
            process_progress.set(0)
    btn_convert.configure(text='เริ่ม', state='normal')

def start_convert_thread():
    btn_convert.configure(text='ตรวจสอบ...', state='disabled')
    convert_thread = threading.Thread(target=convert)
    convert_thread.start()

# Application
lythrum = customtkinter.CTk()

# Title Name
lythrum.title(title_name)

# Font
font_theme_16 = customtkinter.CTkFont(family=font_name, size=16)
font_theme_18 = customtkinter.CTkFont(family=font_name, size=18)
font_theme_24 = customtkinter.CTkFont(family=font_name, size=24)
font_theme_32 = customtkinter.CTkFont(family=font_name, size=32)
font_theme_48 = customtkinter.CTkFont(family=font_name, size=48)
font_theme_52 = customtkinter.CTkFont(family=font_name, size=52)

# Icon
lythrum.iconbitmap(icon_file)

# Display Size
screen_width = lythrum.winfo_screenwidth()
screen_height = lythrum.winfo_screenheight()
position_x = round((screen_width/2) - (display_width/2))
position_y = round((screen_height/2.5) - (display_height/2))
lythrum.geometry(f'{display_width}x{display_height}+{position_x}+{position_y}')
lythrum.minsize(display_width, display_height)

# Responsive Design
lythrum.columnconfigure(0, weight=1)
lythrum.columnconfigure(1, weight=1)
lythrum.columnconfigure(2, weight=1)
lythrum.columnconfigure(3, weight=1)
lythrum.columnconfigure(4, weight=1)
lythrum.rowconfigure(0, weight=1)
lythrum.rowconfigure(1, weight=1)
lythrum.rowconfigure(2, weight=1)
lythrum.rowconfigure(3, weight=1)
lythrum.rowconfigure(4, weight=1)
lythrum.rowconfigure(5, weight=1)
lythrum.rowconfigure(6, weight=1)
lythrum.rowconfigure(7, weight=1)

# Widget
btn_choose_files = customtkinter.CTkButton(command=browse_files_source, master=lythrum, text='นำเข้า', font=font_theme_24)
btn_choose_files.grid(row=0, column=0, padx=10, pady=10, sticky='news')

btn_clear_all_unsuccess = customtkinter.CTkButton(command=clear_all_unsuccess, master=lythrum, text='ล้างทั้งหมด', font=font_theme_24)
btn_clear_all_unsuccess.grid(row=0, column=1, padx=10, pady=10, sticky='news')

folder_destination = customtkinter.StringVar()
btn_choose_folder = customtkinter.CTkButton(command=browse_folder_destination, master=lythrum, text='ปลายทาง', font=font_theme_24)
tooltip_choose_folder = CTkToolTip.CTkToolTip(btn_choose_folder, delay=0.5, message='ยังไม่มีปลายทางที่ระบุ')
btn_choose_folder.grid(row=0, column=3, padx=10, pady=10, sticky='news')

btn_clear_all_success = customtkinter.CTkButton(command=clear_all_success, master=lythrum, text='ล้างทั้งหมด', font=font_theme_24)
btn_clear_all_success.grid(row=0, column=4, padx=10, pady=10, sticky='news')

sf_show_unsuccess = customtkinter.CTkScrollableFrame(master=lythrum, label_font=font_theme_24)
sf_show_unsuccess.grid(row=1, column=0, columnspan=3, rowspan=5, padx=10, pady=10, sticky='news')

sf_show_success = customtkinter.CTkScrollableFrame(master=lythrum, label_font=font_theme_24)
sf_show_success.grid(row=1, column=3, columnspan=3, rowspan=5, padx=10, pady=10, sticky='news')

btn_show_unsuccess = customtkinter.CTkButton(master=lythrum, text='จำนวนไฟล์: 0', font=font_theme_24)
btn_show_unsuccess.grid(row=6, column=0, padx=10, pady=10, sticky='news')

btn_show_success = customtkinter.CTkButton(master=lythrum, text='เสร็จสิ้น: 0', font=font_theme_24)
btn_show_success.grid(row=6, column=3, padx=10, pady=10, sticky='news')

process_progress = customtkinter.CTkProgressBar(master=lythrum, mode='determinate', orientation='horizontal', height=15)
process_progress.grid(row=7, column=0, columnspan=3, padx=10, pady=10, sticky='ew')
process_progress.set(0)

btn_choose_format_all = customtkinter.CTkButton(command=choose_format_all, master=lythrum, text='แปลงทั้งหมดเป็น', font=font_theme_24)
btn_choose_format_all.grid(row=7, column=3, padx=10, pady=10, sticky='news')

btn_convert = customtkinter.CTkButton(command=start_convert_thread, master=lythrum, text='เริ่ม', font=font_theme_24)
btn_convert.grid(row=7, column=4, padx=10, pady=10, sticky='news')

# Start Application
lythrum.mainloop()
