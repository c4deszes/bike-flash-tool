from PyQt6.QtWidgets import *
from PyQt6.QtCore import QThread, pyqtSignal
import time
import logging
import serial.tools.list_ports

from line_flash.flash import FlashTool
from line_protocol.protocol.master import LineMaster
from line_protocol.protocol.transport import LineSerialTransport, LineTransportTimeout

class PortDiscoveryThread(QThread):

    ports_found = pyqtSignal(list)
    stop = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._stopped = False

    def close_thread(self):
        self._stopped = True

    def run(self):
        self.stop.connect(self.close_thread)

        while self._stopped is False:
            ports = [x.device for x in serial.tools.list_ports.comports()]
            self.ports_found.emit(ports)

            time.sleep(5)

class FlashThread(QThread):
    finished = pyqtSignal()
    failed = pyqtSignal()
    progress = pyqtSignal(int, int)
    log_message = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.port = "COM1"
        self.baudrate = 19200
        self.app_address = 0
        self.boot_address = 0xE
        self.serial_number = 0
        self.hex_file = None

    # TODO: might need partial
    def on_progress(self, size, progress, current_address, step_size):
        self.progress.emit(size, progress)

    def run(self):
        try:
            with LineSerialTransport(self.port, baudrate=self.baudrate, one_wire=True) as transport:
                self.log_message.emit(f"Opened port {self.port} at {self.baudrate} bps.")
                master = LineMaster(transport)
                flash_tool = FlashTool(master)

                flash_tool.enter_bootloader(self.boot_address,
                                        app_address=self.app_address if self.app_address != 0 else None,
                                        serial_number=self.serial_number if self.serial_number != 0 else None)
                self.log_message.emit("Entered bootloader.")

                try:
                    flash_tool.flash_hex(self.boot_address, self.hex_file, on_progess=self.on_progress)
                    self.log_message.emit("Flashing complete.")
                except Exception as e:
                    self.log_message.emit(f"Flashing failed: {type(e).__name__}")
                    self.log_message.emit(str(e))
                    self.failed.emit()

                try:
                    flash_tool.exit_bootloader(self.boot_address, app_address=self.app_address if self.app_address != 0 else None)
                    self.log_message.emit("Exited bootloader.")
                except Exception as e:
                    self.log_message.emit(f"Failed to exit bootloader: {type(e).__name__}")
                    self.log_message.emit(str(e))
                    self.failed.emit()

        except Exception as e:
            self.log_message.emit(f"Failure: {type(e).__name__}")
            self.log_message.emit(str(e))
            self.failed.emit()

        self.finished.emit()

port_discovery_thread = PortDiscoveryThread()
threads = {}

def main():
    logging.basicConfig(level=logging.DEBUG)


    app = QApplication([])
    app.setApplicationName("FlashTool")
    window = QWidget()

    #flash_thread = FlashThread()

    main_layout = QVBoxLayout()

    transport_settings_panel = QHBoxLayout()
    transport_settings_group = QGroupBox("Connection settings")
    transport_settings_layout = QHBoxLayout()
    transport_settings_group.setLayout(transport_settings_layout)
    transport_settings_panel.addWidget(transport_settings_group)

    # port selection
    transport_port_combobox = QComboBox()
    ports = serial.tools.list_ports.comports()

    transport_port_combobox.addItems([x.device for x in ports])  # TODO: dynamic

    transport_baud_spinbox = QSpinBox()
    transport_baud_spinbox.setMaximum(19200)
    transport_baud_spinbox.setMinimum(4800)
    transport_baud_spinbox.setSingleStep(4800)
    transport_baud_spinbox.setSuffix(" bps")
    transport_baud_spinbox.setValue(19200)

    transport_settings_layout.addWidget(transport_port_combobox)
    transport_settings_layout.addWidget(transport_baud_spinbox)

    connection_settings_panel = QHBoxLayout()

    # Boot address
    boot_address_group = QGroupBox("BootAddress")
    boot_address_layout = QHBoxLayout()
    boot_address_group.setLayout(boot_address_layout)
    boot_address_spinbox = QSpinBox()
    boot_address_spinbox.setMaximum(0xF)
    boot_address_spinbox.setMinimum(0)
    boot_address_spinbox.setSingleStep(1)
    boot_address_spinbox.setPrefix("0x")
    boot_address_spinbox.setValue(0xE)
    boot_address_spinbox.setWhatsThis("Diagnostic address in boot mode")
    boot_address_spinbox.setDisplayIntegerBase(16)
    boot_address_layout.addWidget(boot_address_spinbox)

    # App address
    app_address_group = QGroupBox("AppAddress")
    app_address_layout = QHBoxLayout()
    app_address_group.setLayout(app_address_layout)
    app_address_spinbox = QSpinBox()
    app_address_spinbox.setMaximum(0xF)
    app_address_spinbox.setMinimum(0)
    app_address_spinbox.setSingleStep(1)
    app_address_spinbox.setPrefix("0x")
    app_address_spinbox.setValue(0)
    app_address_spinbox.setWhatsThis("Application diagnostic address")
    app_address_spinbox.setDisplayIntegerBase(16)
    app_address_layout.addWidget(app_address_spinbox)

    # Serial number
    serial_number_group = QGroupBox("SerialNumber")
    serial_number_layout = QHBoxLayout()
    serial_number_group.setLayout(serial_number_layout)
    serial_number_input = QLineEdit()
    serial_number_input.setPlaceholderText("Serial number")
    serial_number_layout.addWidget(serial_number_input)

    connection_settings_panel.addWidget(boot_address_group)
    connection_settings_panel.addWidget(app_address_group)
    connection_settings_panel.addWidget(serial_number_group)

    # File selector
    file_selector_group = QGroupBox("Program")
    file_selector_layout = QHBoxLayout()
    file_selector_group.setLayout(file_selector_layout)

    file_path_input = QLineEdit()
    file_path_input.setPlaceholderText("Select a file...")

    file_select_button = QPushButton("Choose")
    file_select_button.clicked.connect(lambda: file_path_input.setText(QFileDialog.getOpenFileName(filter='*.hex')[0]))

    file_selector_layout.addWidget(file_path_input)
    file_selector_layout.addWidget(file_select_button)

    # Flash button
    flash_button = QPushButton("Flash")

    # Logs
    log_textedit = QTextEdit()
    log_textedit.setReadOnly(True)

    # Progress bar
    progress_bar = QProgressBar()
    progress_bar.setRange(0, 100)
    progress_bar.setValue(0)
    progress_bar.setTextVisible(True)

    # Adding everything to main panel
    main_layout.addLayout(transport_settings_panel)
    main_layout.addLayout(connection_settings_panel)
    main_layout.addWidget(file_selector_group)
    main_layout.addWidget(flash_button)
    main_layout.addWidget(log_textedit)
    main_layout.addWidget(progress_bar)

    def lock_ui():
        flash_button.setEnabled(False)
        transport_port_combobox.setEnabled(False)
        transport_baud_spinbox.setEnabled(False)
        boot_address_spinbox.setEnabled(False)
        app_address_spinbox.setEnabled(False)
        serial_number_input.setEnabled(False)
        file_path_input.setEnabled(False)
        file_select_button.setEnabled(False)
    
    def unlock_ui():
        flash_button.setEnabled(True)
        transport_port_combobox.setEnabled(True)
        transport_baud_spinbox.setEnabled(True)
        boot_address_spinbox.setEnabled(True)
        app_address_spinbox.setEnabled(True)
        serial_number_input.setEnabled(True)
        file_path_input.setEnabled(True)
        file_select_button.setEnabled(True)

    def clear_logs():
        log_textedit.clear()

    def on_log(message):
        log_textedit.append(message)

    def on_progress(size, progress):
        progress_bar.setValue(int(progress / size * 100))

    def convert_to_int(value):
        try:
            return int(value, 0)
        except ValueError:
            return None

    def end_flash():
        unlock_ui()

    def closeEvent(event):
        if 'flash' in threads and threads['flash'].isRunning():
            reply = QMessageBox.question(window, 'Message',
                                            "Flashing is in progress. Are you sure you want to quit?",
                                            QMessageBox.StandardButton.Yes, QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                event.accept()
            else:
                event.ignore()
        else:
            port_discovery_thread.stop.emit()

            event.accept()

    def set_ports(port_list):
        transport_port_combobox.clear()
        transport_port_combobox.addItems(port_list)

    def start_flash():
        clear_logs()
        lock_ui()

        flash_thread = FlashThread()
        threads['flash'] = flash_thread     # prevents garbage collection

        flash_thread.port = transport_port_combobox.currentText()
        flash_thread.baudrate = transport_baud_spinbox.value()
        flash_thread.app_address = app_address_spinbox.value() if app_address_spinbox.value() != 0 else None
        flash_thread.boot_address = boot_address_spinbox.value() if boot_address_spinbox.value() != 0 else None
        flash_thread.serial_number = convert_to_int(serial_number_input.text())
        flash_thread.hex_file = file_path_input.text()

        flash_thread.log_message.connect(on_log)
        flash_thread.progress.connect(on_progress)
        flash_thread.finished.connect(end_flash)
        flash_thread.start()

    flash_button.clicked.connect(start_flash)

    port_discovery_thread.ports_found.connect(set_ports)

    port_discovery_thread.start()

    window.closeEvent = closeEvent
    window.setLayout(main_layout)
    window.show()
    app.exec()

if __name__ == '__main__':
    main()
