import customtkinter
from tkinter import messagebox
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from threading import Thread
import serial.tools.list_ports
import serial
import logging

from line_flash.flash import FlashTool
from line_protocol.protocol.master import LineMaster
from line_protocol.protocol.transport import LineSerialTransport, LineTransportTimeout

class App(customtkinter.CTk):

    def __init__(self):
        super().__init__()

        logging.basicConfig(level=logging.DEBUG)

        # Window settings
        self.title("LINE FlashTool")
        self.geometry("400x400")
        self.grid_columnconfigure((0), weight=1)

        ports = serial.tools.list_ports.comports()

        self.grid_rowconfigure((0, ), weight=1)
        self.grid_rowconfigure((1, ), weight=0)

        self.frame_Settings = customtkinter.CTkFrame(self)
        self.frame_Settings.grid(row=0, column=0, sticky='new')
        self.frame_Settings.grid_columnconfigure((0, ), weight=1)

        self.frame_Config = customtkinter.CTkFrame(self.frame_Settings)
        self.frame_Config.grid(row=0, column=0, sticky='ew')

        self.combo_PortSelect = customtkinter.CTkComboBox(self.frame_Config, values=[x.device for x in ports])
        self.combo_PortSelect.grid(row=0, column=0, sticky='w', padx=10, pady=10)

        self.combo_BaudSelect = customtkinter.CTkComboBox(self.frame_Config, values=['9600', '19200', '56700', '115200'])
        self.combo_BaudSelect.grid(row=0, column=1, sticky='e', padx=10, pady=10)
        self.combo_BaudSelect.set('19200')

        self.frame_File = customtkinter.CTkFrame(self.frame_Settings)
        self.frame_File.grid(row=1, column=0, sticky='ew')
        self.frame_File.grid_columnconfigure(0, weight=1)
        self.frame_File.grid_columnconfigure(1, weight=0)

        self.text_ProgramFile = customtkinter.CTkLabel(self.frame_File, text='No file selected')
        self.text_ProgramFile.grid(row=0, column=0, sticky='ew', padx=10, pady=10)

        self.button_ProgramFileSelect = customtkinter.CTkButton(self.frame_File, text='Select', command=self.select_program, width=70)
        self.button_ProgramFileSelect.grid(row=0, column=1, sticky='ew', padx=10, pady=10)

        integer_validator = (self.register(self.validate_integer))

        # Application address selection
        self.frame_App = customtkinter.CTkFrame(self.frame_Settings)
        self.frame_App.grid(row=2, column=0, sticky='we')
        self.frame_App.grid_columnconfigure((1, ), weight=1)

        self.label_AppAddress = customtkinter.CTkLabel(self.frame_App, text='App. address:')
        self.label_AppAddress.grid(row=0, column=0, sticky='ew', padx=10, pady=10)

        self.input_AppAddress = customtkinter.CTkEntry(self.frame_App, placeholder_text='N/A', validate='all', validatecommand=(integer_validator, '%P'))
        self.input_AppAddress.grid(row=0, column=1, sticky='ew', padx=10, pady=10)

        self.button_ClearAppAddress = customtkinter.CTkButton(self.frame_App, text='Clear', command=self.clear_app_address, width=70)
        self.button_ClearAppAddress.grid(row=0, column=2, sticky='ew', padx=10, pady=10)

        # Serial number selection
        self.frame_Serial = customtkinter.CTkFrame(self.frame_Settings)
        self.frame_Serial.grid(row=3, column=0, sticky='ew')
        self.frame_Serial.grid_columnconfigure((1, ), weight=1)

        self.label_SerialNumber = customtkinter.CTkLabel(self.frame_Serial, text='Serial:')
        self.label_SerialNumber.grid(row=0, column=0, sticky='ew', padx=10, pady=10)

        self.input_SerialNumber = customtkinter.CTkEntry(self.frame_Serial, placeholder_text='N/A', validate='all', validatecommand=(integer_validator, '%P'))
        self.input_SerialNumber.grid(row=0, column=1, sticky='ew', padx=10, pady=10)

        self.button_ClearSerialNumber = customtkinter.CTkButton(self.frame_Serial, text='Clear', command=self.clear_serial_number, width=70)
        self.button_ClearSerialNumber.grid(row=0, column=2, sticky='ew', padx=10, pady=10)

        # Uploading
        self.frame_Upload = customtkinter.CTkFrame(self)
        self.frame_Upload.grid(row=1, column=0, sticky='news')
        self.frame_Upload.grid_columnconfigure((0, ), weight=1)

        self.message_Logs = customtkinter.CTkTextbox(self.frame_Upload, state='disabled', height=100)
        self.message_Logs.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky='ew')

        # TODO: implement https://stackoverflow.com/questions/68738022/how-to-create-a-simple-progress-bar-loop-in-tkinter
        self.progress_Flash = customtkinter.CTkProgressBar(self.frame_Upload, mode='determinate')
        self.progress_Flash.grid(row=1, column=0, sticky='ew', padx=10, pady=10)

        self.button_Flash = customtkinter.CTkButton(self.frame_Upload, text='Flash', width=10, command=self.flash_program)
        self.button_Flash.grid(row=1, column=1, sticky='ew', padx=10, pady=10)

        self.protocol('WM_DELETE_WINDOW', self.on_window_close)

    def select_program(self):
        program_path = customtkinter.filedialog.askopenfilename(filetypes=[('Intel HEX', 'hex')])
        self.text_ProgramFile.configure(require_redraw=True, text=program_path)

    def validate_integer(self, value):
        # TODO: implement
        return True

    def clear_app_address(self):
        self.input_AppAddress.delete(0, customtkinter.END)

    def clear_serial_number(self):
        self.input_SerialNumber.delete(0, customtkinter.END)

    def log_message(self, text):
        self.message_Logs.configure(state='normal')
        self.message_Logs.insert(customtkinter.END, text)
        self.message_Logs.insert(customtkinter.END, "\n")
        self.message_Logs.configure(state='disabled')

    def clear_logs(self):
        self.message_Logs.configure(state='normal')
        self.message_Logs.delete('0.0', customtkinter.END)
        self.message_Logs.configure(state='disabled')

    def set_progress(self, progress, maximum):
        self.progress_Flash['value'] = 1
        self.progress_Flash['maximum'] = 1
        self.progress_Flash.update()
        #self.progress_Flash.configure(require_redraw=True, background='blue')

    def set_progress_error(self):
        self.progress_Flash['value'] = 1
        self.progress_Flash['maximum'] = 1
        self.progress_Flash.update()
        #self.progress_Flash.configure(require_redraw=True, background='red')

    def flash_program(self):
        # check conditions
        # if no file -> error
        # if the file doesn't exist -> error
        #messagebox.showerror('Error', 'No program has been selected.')

        # if no serial and no app -> error

        program = self.text_ProgramFile.cget('text')
        port = self.combo_PortSelect.get()
        baudrate = self.combo_BaudSelect.get()
        app_address = self.input_AppAddress.get()
        serial_number = self.input_SerialNumber.get()

        if not app_address.strip() and not serial_number.strip():
            return

        # At this point commit to flashing
        self.button_Flash.configure(state='disabled')
        self.clear_logs()

        # 
        try:
            with LineSerialTransport(port, baudrate=baudrate, one_wire=True) as transport:
                master = LineMaster(transport)
                flash_tool = FlashTool(master)

                self.log_message('Entering boot mode.')
                flash_tool.enter_bootloader(0xE,
                                            int(app_address, base=0) if app_address.strip() else None,
                                            int(serial_number, base=0) if serial_number.strip() else None)

                try:
                    self.log_message(f"Flashing '{program}'")
            #     #flash_tool.flash_hex(0xE, self.program_path)
                except FileNotFoundError as exc:
                    self.log_message(f"{exc}")
                    self.set_progress_error()

                self.log_message(f"Exiting boot mode.")
                flash_tool.exit_bootloader(0xE,
                                            int(app_address, base=0) if app_address.strip() else None)

        except serial.SerialException as exc:
            self.log_message(f"{exc}")
            self.set_progress_error()

        self.button_Flash.configure(state='normal')
        # scenarios
        # 1. serial port cannot be used
        # 2. boot entry fails
        # 3. flash write fails
        # 4. boot exit fails
        # 5. communication errors
        # 6. file doesnt exist, or bad

        pass

    def on_window_close(self):
        if messagebox.askokcancel('Quit', 'A measurement is running, are you sure you want to quit?'):
            self.destroy()

def main():
    app = App()
    #app.after(10, app.update_ui)
    app.mainloop()

    return 0

if __name__ == '__main__':
    main()
