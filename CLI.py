import sys
import os
import time
import base64
import hashlib
import secrets
from cryptography.fernet import Fernet, InvalidToken # <-- CORRECTED IMPORT
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QIcon, QKeySequence, QGuiApplication
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QTextEdit,
    QFileDialog,
    QMessageBox,
    QWidget,
    QVBoxLayout,
    QLabel,
    QStatusBar,
    QToolBar,
    QDialog,
    QTextBrowser,
    QInputDialog,
    QPushButton,
    QMenuBar,
    QMenu,
    QToolButton, 
)


APP_TITLE = "VoidRoot - CLI "
APP_VERSION = "2.3.3"
FILE_EXTENSION = ".vort"


def sha256_hex(data: str) -> str:
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def encode_payload(text: str) -> str:
    return base64.b64encode(text.encode("utf-8")).decode("utf-8")


def decode_payload(payload: str) -> str:
    return base64.b64decode(payload.encode("utf-8")).decode("utf-8")


def get_next_default_filename() -> str:
    desktop = Path.home() / "Desktop"
    counter = 1

    while True:
        candidate = desktop / f"New CLI {counter}{FILE_EXTENSION}"
        if not candidate.exists():
            return str(candidate)
        counter += 1


class AboutDialog(QDialog):
    def __init__(self, about_text: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About VORT")
        self.resize(520, 340)

        layout = QVBoxLayout(self)

        browser = QTextBrowser()
        browser.setOpenExternalLinks(True)
        browser.setHtml(about_text)

        layout.addWidget(browser)


class VortMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.current_file_path = None
        self.editor_locked = False
        self.unsafe_keywords = {
            "ghidra",
            "ida",
            "x64dbg",
            "x32dbg",
            "ollydbg",
            "radare2",
            "frida",
            "dnspy",
            "debug",
            "debugger",
            "reverse",
            "reverse engineering",
            "config script",
            "hook",
            "inject",
            "patch",
            "trace",
            "disasm",
            "decompile",
            "memory dump",
            "analyze binary",
        }

        self.about_text = """
        <h2>VORT Editor</h2>
        <p><b>Version:</b>2.3.3</p>
        <p>This software is designed to create, open, validate, and manage VORT files.</p>
        <p><b>Developer:</b>Behnood Shafiei</p>
        <p>If you have any issuse check the github repo .</p>
        <p>https://github.com/Behnooddev/Python-CLI.git</p>
        """

        self.setWindowTitle(f"{APP_TITLE} {APP_VERSION}")
        self.resize(980, 640)
        self.setMinimumSize(760, 500)

        self.editor = QTextEdit()
        self.editor.setAcceptRichText(False)
        self.editor.setPlaceholderText("Type or load your VORT content here...")
        self.editor.textChanged.connect(self.update_status_info)

        self.info_label = QLabel("Ready")
        self.info_label.setObjectName("infoLabel")

        central = QWidget()
        central_layout = QVBoxLayout(central)
        central_layout.addWidget(self.info_label)
        central_layout.addWidget(self.editor)
        self.setCentralWidget(central)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        self.create_actions()
        self.create_menus()
        self.create_toolbar()
        self.apply_hacker_theme()
        self.update_status_info()

        self.app_data_roaming = str(Path.home() / "AppData/Roaming/voidroot/CLI")
        self.app_data_local = str(Path.home() / "AppData/Local/voidroot/CLI")

        # Ensure directories exist
        os.makedirs(self.app_data_roaming, exist_ok=True)
        os.makedirs(self.app_data_local, exist_ok=True)
        # --- End New Path Definitions ---


    def create_actions(self):
        self.new_action = QAction("New", self)
        self.new_action.setShortcut(QKeySequence.New)
        self.new_action.triggered.connect(self.new_file)

        self.open_action = QAction("Open", self)
        self.open_action.setShortcut(QKeySequence.Open)
        self.open_action.triggered.connect(self.open_vort_file_dialog)

        self.save_action = QAction("Save", self)
        self.save_action.setShortcut(QKeySequence.Save)
        self.save_action.triggered.connect(self.save_vort_file)

        self.save_as_action = QAction("Save As", self)
        self.save_as_action.setShortcut(QKeySequence.SaveAs)
        self.save_as_action.triggered.connect(self.save_vort_file_as)

        self.exit_action = QAction("Exit", self)
        self.exit_action.setShortcut(QKeySequence.Quit)
        self.exit_action.triggered.connect(self.close)

        self.undo_action = QAction("Undo", self)
        self.undo_action.setShortcut(QKeySequence.Undo)
        self.undo_action.triggered.connect(self.editor.undo)

        self.redo_action = QAction("Redo", self)
        self.redo_action.setShortcut(QKeySequence.Redo)
        self.redo_action.triggered.connect(self.editor.redo)

        self.cut_action = QAction("Cut", self)
        self.cut_action.setShortcut(QKeySequence.Cut)
        self.cut_action.triggered.connect(self.editor.cut)

        self.copy_action = QAction("Copy", self)
        self.copy_action.setShortcut(QKeySequence.Copy)
        self.copy_action.triggered.connect(self.editor.copy)

        self.paste_action = QAction("Paste", self)
        self.paste_action.setShortcut(QKeySequence.Paste)
        self.paste_action.triggered.connect(self.editor.paste)

        self.select_all_action = QAction("Select All", self)
        self.select_all_action.setShortcut(QKeySequence.SelectAll)
        self.select_all_action.triggered.connect(self.editor.selectAll)

        self.validate_action = QAction("Validate Buffer", self)
        self.validate_action.triggered.connect(self.validate_current_text)

        self.about_action = QAction("About", self)
        self.about_action.triggered.connect(self.show_about_dialog)


        self.encode_action = QAction("Encode", self)
        self.encode_action.triggered.connect(self.encode_content_action) # <-- CORRECTED


        self.decode_action = QAction("Decode", self)
        self.decode_action.triggered.connect(self.decode_content_dialog) # We'll define this method


        self.save_plain_action = QAction("Save as Plaintext", self)
        self.save_plain_action.triggered.connect(lambda: self.save_vort_file(save_encrypted=False))

        self.save_encrypted_action = QAction("Save Encrypted", self)
        self.save_encrypted_action.triggered.connect(lambda: self.save_vort_file(save_encrypted=True))


        self.lock_action = QAction("Lock/Unlock", self)
        self.lock_action.triggered.connect(self.toggle_editor_lock)

    def create_menus(self):
        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu("File")
        file_menu.addAction(self.new_action)
        file_menu.addAction(self.open_action)
        file_menu.addAction(self.save_action)
        file_menu.addAction(self.save_as_action)
        # --- Add Save Type options to File Menu ---
        file_menu.addAction(self.save_plain_action)
        file_menu.addAction(self.save_encrypted_action)
        # --- End Add Save Type options ---

        file_menu.addSeparator()
        file_menu.addAction(self.exit_action)

        edit_menu = menu_bar.addMenu("Edit")
        edit_menu.addAction(self.undo_action)
        edit_menu.addAction(self.redo_action)
        edit_menu.addSeparator()
        edit_menu.addAction(self.cut_action)
        edit_menu.addAction(self.copy_action)
        edit_menu.addAction(self.paste_action)
        edit_menu.addSeparator()
        edit_menu.addAction(self.select_all_action)

        tools_menu = menu_bar.addMenu("Tools")
        tools_menu.addAction(self.validate_action)
        tools_menu.addAction(self.validate_action)
        tools_menu.addSeparator() 
        tools_menu.addAction(self.encode_action)
        tools_menu.addAction(self.decode_action)
        tools_menu.addAction(self.lock_action)

        help_menu = menu_bar.addMenu("Help")
        help_menu.addAction(self.about_action)

    def create_toolbar(self):
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        self.addToolBar(Qt.TopToolBarArea, toolbar)

        toolbar.addAction(self.new_action)
        toolbar.addAction(self.open_action)
        toolbar.addAction(self.save_action)
        toolbar.addSeparator()
        toolbar.addAction(self.cut_action)
        toolbar.addAction(self.copy_action)
        toolbar.addAction(self.paste_action)
        toolbar.addSeparator()
        toolbar.addAction(self.undo_action)
        toolbar.addAction(self.redo_action)
        # --- Add Encryption/Decryption to Toolbar ---
        toolbar.addSeparator()
        toolbar.addAction(self.encode_action)
        toolbar.addAction(self.decode_action)
        # --- End Add Encryption/Decryption to Toolbar ---

        toolbar.addAction(self.lock_action)

        toolbar.addSeparator()
        toolbar.addAction(self.about_action)

    def apply_hacker_theme(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #07110d;
            }

            QWidget {
                background-color: #07110d;
                color: #7CFFB2;
                font-family: Consolas, 'Courier New', monospace;
                font-size: 13px;
            }

            QMenuBar {
                background-color: #081712;
                color: #74ffae;
                border-bottom: 1px solid #0f5c3d;
            }

            QMenuBar::item {
                background: transparent;
                padding: 8px 12px;
            }

            QMenuBar::item:selected {
                background: #0f2e21;
                color: #a8ffcb;
            }

            QMenu {
                background-color: #081712;
                border: 1px solid #0f5c3d;
                padding: 4px;
            }

            QMenu::item {
                padding: 8px 20px;
                background-color: transparent;
            }

            QMenu::item:selected {
                background-color: #103726;
                color: #c8ffdf;
            }

            QToolBar {
                background-color: #081712;
                border-bottom: 1px solid #0f5c3d;
                spacing: 6px;
                padding: 6px;
            }

            QToolButton {
                background-color: #0a1d16;
                color: #7CFFB2;
                border: 1px solid #16573c;
                border-radius: 6px;
                padding: 6px 10px;
            }

            QToolButton:hover {
                background-color: #103726;
                border: 1px solid #23b26b;
            }

            QTextEdit {
                background-color: #020806;
                color: #8dffbd;
                border: 1px solid #14583a;
                selection-background-color: #1a7f52;
                selection-color: #eafff4;
                padding: 10px;
            }

            QLabel#infoLabel {
                color: #59d690;
                padding: 4px 2px;
            }

            QStatusBar {
                background-color: #081712;
                color: #74ffae;
                border-top: 1px solid #0f5c3d;
            }

            QMessageBox {
                background-color: #081712;
            }

            QPushButton {
                background-color: #0b241a;
                color: #8dffbd;
                border: 1px solid #1a7f52;
                padding: 6px 12px;
                border-radius: 6px;
            }

            QPushButton:hover {
                background-color: #103726;
            }
        """)

    def update_status_info(self):
        text = self.editor.toPlainText()
        char_count = len(text)
        line_count = self.editor.document().blockCount()
        current_name = self.current_file_path if self.current_file_path else "Unsaved buffer"

        self.info_label.setText(
            f"Target: {current_name} | Characters: {char_count} | Lines: {line_count}"
        )
        self.status_bar.showMessage("Ready", 2000)

    def is_sensitive_content(self, text: str) -> str | None:
        lower_text = text.lower()
        for keyword in self.unsafe_keywords:
            if keyword in lower_text:
                return keyword
        return None

    def new_file(self):
        self.editor.clear()
        self.current_file_path = None
        self.status_bar.showMessage("New buffer created", 3000)
        self.update_status_info()

    def build_vort_content(self, text: str) -> str:
        # This function builds the STANDARD VORT structure.
        # Encryption is handled separately in save_to_path.
        salt = secrets.token_hex(8)
        payload = encode_payload(text) # base64 encode
        file_hash = sha256_hex(salt + text) # hash of original text

        content = (
            "VORT1\n"
            f"hash: {file_hash}\n"
            f"salt: {salt}\n"
            f"payload: {payload}\n"
        )
        return content

        salt = secrets.token_hex(8)
        payload = encode_payload(text)
        file_hash = sha256_hex(salt + text)

        content = (
            "VORT1\n"
            f"hash: {file_hash}\n"
            f"salt: {salt}\n"
            f"payload: {payload}\n"
        )
        return content

    def parse_vort(self, content: str) -> dict:
        lines = [line.strip() for line in content.splitlines() if line.strip()]
        if not lines or lines[0] != "VORT1":
            return {}

        data = {}
        for line in lines[1:]:
            if ":" not in line:
                continue
            key, value = line.split(":", 1)
            data[key.strip().lower()] = value.strip()
        return data

    def validate_current_text(self):
        text = self.editor.toPlainText()
        if not text.strip():
            QMessageBox.information(self, "Validation", "The editor is empty.")
            return

        blocked = self.is_sensitive_content(text)
        if blocked:
            QMessageBox.warning(
                self,
                "Blocked Content",
                f"Sensitive content detected: {blocked}\nOperation denied."
            )
            return

        QMessageBox.information(
            self,
            "Validation",
            "Buffer check completed successfully."
        )

    def open_vort_file_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open VORT File",
            "",
            "VORT Files (*.vort)"
        )

        if file_path:
            self.open_vort_file_direct(file_path)

    def open_vort_file_direct(self, file_path: str):
        try:
            if not file_path.lower().endswith(FILE_EXTENSION):
                # Handle case where an encrypted file might not have .vort extension
                if not file_path.lower().endswith(".enc"): # Example for encrypted files
                    QMessageBox.warning(self, "Invalid File", f"Unsupported file type. Expected *.vort or known encrypted format. Received: {os.path.basename(file_path)}")
                    return

            with open(file_path, "r", encoding="utf-8") as file:
                raw_content = file.read()

            # --- Attempt to parse as VORT1 first ---
            data = self.parse_vort(raw_content)
            file_hash = data.get("hash", "")
            salt = data.get("salt", "")
            payload = data.get("payload", "")

            decoded_text = ""
            is_vort_format = bool(data and "hash" in data and "salt" in data and "payload" in data)

            if is_vort_format:
                # It seems to be a standard VORT file
                if not file_hash or not salt or not payload:
                    QMessageBox.warning(self, "Invalid File", "Missing required VORT fields.")
                    return

                try:
                    decoded_text = decode_payload(payload) # Decode the base64 payload
                except Exception:
                    QMessageBox.critical(self, "Decoding Error", "Failed to decode VORT payload. File might be corrupted.")
                    return

                blocked_decoded = self.is_sensitive_content(decoded_text)
                if blocked_decoded:
                    QMessageBox.critical(
                        self,
                        "Security Block",
                        f"Suspicious keyword detected in decoded content: {blocked_decoded}\nFile rejected."
                    )
                    return

                computed_hash = sha256_hex(salt + decoded_text)
                if computed_hash != file_hash:
                    QMessageBox.critical(
                        self,
                        "Integrity Error",
                        "Hash validation failed. The file may be corrupted or modified."
                    )
                    return
                elif not raw_content.strip():
                    self.editor.clear()
                    self.current_file_path = file_path

                    self.status_bar.showMessage(
                        f"New empty VORT file opened: {os.path.basename(file_path)}",
                        4000
                    )

                    self.update_status_info()
                    return
            else:
                # If not standard VORT, try to decrypt it as an encrypted file
                # This requires the user to provide the key if they open an encrypted file directly.
                # For now, we'll assume if it's NOT VORT1, it might be encrypted and prompt for key.
                # THIS IS A SIMPLIFICATION. A robust app might have a separate "Open Encrypted" option.

                # Check if the raw content looks like base64 or a Fernet token
                # This is heuristic and can fail.
                try:
                    # Try to decrypt using the last used key, or prompt user
                    # Prompting is safer for direct file opens.
                    key_input, ok = QInputDialog.getText(self, "Open Encrypted File", "File is not standard VORT. Enter encryption key to decrypt:")
                    if ok and key_input:
                        fernet = Fernet(key_input.encode())
                        decrypted_bytes = fernet.decrypt(raw_content.encode())
                        decoded_text = decrypted_bytes.decode()

                        # Check decoded content for sensitivity
                        blocked_decoded = self.is_sensitive_content(decoded_text)
                        if blocked_decoded:
                            QMessageBox.critical(
                                self,
                                "Security Block",
                                f"Suspicious keyword detected in decoded content: {blocked_decoded}\nFile rejected."
                            )
                            return

                        # If we successfully decrypted, it's considered opened.
                        # We don't have hash/salt for these.
                        self.status_bar.showMessage(f"Opened (Decrypted): {os.path.basename(file_path)}", 4000)

                    else:
                        QMessageBox.warning(self, "Decryption Cancelled", "File could not be opened without a key.")
                        return

                except InvalidToken:
                    QMessageBox.critical(self, "Decryption Error", "Invalid key or corrupted data. Could not decrypt file.")
                    return
                except Exception as e:
                    QMessageBox.critical(self, "Open Error", f"An unexpected error occurred trying to open/decrypt file:\n{e}")
                    return

            # If we reached here, decoded_text contains the content
            self.editor.setPlainText(decoded_text)
            self.current_file_path = file_path
            self.status_bar.showMessage(f"Opened: {os.path.basename(file_path)}", 4000)
            self.update_status_info()

        except Exception as error:
            QMessageBox.critical(self, "Open Error", f"Failed to open file:\n{error}")
            self.status_bar.showMessage("Open failed.", 5000)

        try:
            if not file_path.lower().endswith(FILE_EXTENSION):
                QMessageBox.warning(self, "Invalid File", "Only .vort files are supported.")
                return

            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()

            blocked = self.is_sensitive_content(content)
            if blocked:
                QMessageBox.critical(
                    self,
                    "Security Block",
                    f"Suspicious keyword detected in file content: {blocked}\nFile rejected."
                )
                return

            data = self.parse_vort(content)
            if not data:
                QMessageBox.warning(self, "Invalid File", "The VORT file structure is invalid.")
                return

            file_hash = data.get("hash", "")
            salt = data.get("salt", "")
            payload = data.get("payload", "")

            if not file_hash or not salt or not payload:
                QMessageBox.warning(self, "Invalid File", "Missing required VORT fields.")
                return

            decoded_text = decode_payload(payload)

            blocked_decoded = self.is_sensitive_content(decoded_text)
            if blocked_decoded:
                QMessageBox.critical(
                    self,
                    "Security Block",
                    f"Suspicious keyword detected in decoded content: {blocked_decoded}\nFile rejected."
                )
                return

            computed_hash = sha256_hex(salt + decoded_text)
            if computed_hash != file_hash:
                QMessageBox.critical(
                    self,
                    "Integrity Error",
                    "Hash validation failed. The file may be corrupted or modified."
                )
                return

            self.editor.setPlainText(decoded_text)
            self.current_file_path = file_path
            self.status_bar.showMessage(f"Opened: {os.path.basename(file_path)}", 4000)
            self.update_status_info()

        except Exception as error:
            QMessageBox.critical(self, "Open Error", f"Failed to open file:\n{error}")

    def save_vort_file(self, save_encrypted: bool = False): # Add parameter here
        if self.current_file_path:
            self.save_to_path(self.current_file_path, save_encrypted=save_encrypted) # Pass parameter
        else:
            self.save_vort_file_as(save_encrypted=save_encrypted) # Pass parameter to save_as

    def save_vort_file_as(self, save_encrypted: bool = False):
        default_name = get_next_default_filename()

        save_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save VORT File",
            default_name,
            "VORT Files (*.vort)"
        )

        if save_path:
            if not save_path.lower().endswith(FILE_EXTENSION):
                save_path += FILE_EXTENSION

            self.save_to_path(save_path, save_encrypted=save_encrypted)
            
    def generate_and_show_key(self) -> str:
        key = Fernet.generate_key()
        key_str = key.decode()

        # Use a dialog to display the key, ensuring it's shown only once
        dialog = QDialog(self)
        dialog.setWindowTitle("Generated Encryption Key")
        dialog.setModal(True)
        dialog.resize(500, 200)

        layout = QVBoxLayout(dialog)

        warning_label = QLabel("<b>IMPORTANT: This key will be shown ONLY ONCE. Save it securely NOW!</b>")
        warning_label.setStyleSheet("color: red; font-weight: bold;")
        layout.addWidget(warning_label)

        key_display = QLabel(f"<p style='font-family: Consolas, monospace; background-color: #020806; color: #8dffbd; padding: 10px; border: 1px solid #14583a;'>{key_str}</p>")
        key_display.setWordWrap(True)
        layout.addWidget(key_display)

        copy_button = QPushButton("Copy Key")

        def copy_key():
            QGuiApplication.clipboard().setText(key_str)
            copy_button.setText("Copied ✓")

        copy_button.clicked.connect(copy_key)

        layout.addWidget(copy_button)

        ok_button = QPushButton("OK, I have saved the key")
        ok_button.clicked.connect(dialog.accept)
        layout.addWidget(ok_button)

        dialog.exec()

        if dialog.result() == QDialog.Accepted:
            return key_str
        else:
            # If dialog is closed without clicking OK, it's problematic.
            # You might want to re-prompt or handle this case more robustly.
            QMessageBox.warning(self, "Key Not Saved", "The key was not saved. Please re-generate if needed.")
            return "" # Return empty if not confirmed

    def save_to_path(self, path: str, save_encrypted: bool = False): # Add parameter here
        try:
            text = self.editor.toPlainText()

            if not text.strip():
                QMessageBox.warning(self, "Empty Content", "The editor is empty.")
                return

            # Check for sensitive content BEFORE building VORT structure
            blocked = self.is_sensitive_content(text)
            if blocked:
                QMessageBox.critical(
                    self,
                    "Security Block",
                    f"Sensitive keyword detected: {blocked}\nSave operation denied."
                )
                return

            # --- Decide whether to build VORT content or just save raw text ---
            content_to_save = ""
            if save_encrypted:
                # If saving as encrypted, we need to encode the content FIRST
                # This means the file saved will be base64 encoded payload, NOT VORT1 structure
                # Or we can encrypt the VORT structure itself. Let's go with encrypting VORT structure.

                # First, build the standard VORT content
                vort_content = self.build_vort_content(text)
                content_to_save = vort_content # This will be encrypted

                # Now, generate a key and encrypt the VORT content
                key = self.generate_and_show_key() # This shows the key for decryption later
                if not key:
                    QMessageBox.warning(self, "Save Cancelled", "Encryption key not saved. File not saved as encrypted.")
                    return

                fernet = Fernet(key.encode())
                encrypted_bytes = fernet.encrypt(vort_content.encode())
                content_to_save = encrypted_bytes.decode() # Save the encrypted string

                # Update status bar about encryption
                self.status_bar.showMessage(f"Saved Encrypted: {os.path.basename(path)}", 4000)

            else: # Save as Plaintext (standard VORT structure)
                content_to_save = self.build_vort_content(text)
                self.status_bar.showMessage(f"Saved Plaintext: {os.path.basename(path)}", 4000)

            # --- Write the content to the file ---
            with open(path, "w", encoding="utf-8") as file:
                file.write(content_to_save)

            self.current_file_path = path

            # --- Create Encrypted Backup ---
            # Backup is always created, encrypted, in Local AppData, regardless of save type
            self.create_encrypted_backup(path)

            self.update_status_info()

        except Exception as error:
            QMessageBox.critical(self, "Save Error", f"Failed to save file:\n{error}")
            self.status_bar.showMessage("Save failed.", 5000)

        try:
            text = self.editor.toPlainText()

            if not text.strip():
                QMessageBox.warning(self, "Empty Content", "The editor is empty.")
                return

            blocked = self.is_sensitive_content(text)
            if blocked:
                QMessageBox.critical(
                    self,
                    "Security Block",
                    f"Sensitive keyword detected: {blocked}\nSave operation denied."
                )
                return

            content = self.build_vort_content(text)

            with open(path, "w", encoding="utf-8") as file:
                file.write(content)

            self.current_file_path = path
            self.status_bar.showMessage(f"Saved: {os.path.basename(path)}", 4000)
            self.update_status_info()

        except Exception as error:
            QMessageBox.critical(self, "Save Error", f"Failed to save file:\n{error}")

    def encode_content_action(self):
        current_text = self.editor.toPlainText()
        if not current_text.strip():
            QMessageBox.warning(self, "Empty Content", "The editor is empty. Nothing to encode.")
            return

        key = self.generate_and_show_key() # Get the key from the secure display

        if not key: # If user closed the key dialog without saving
            self.status_bar.showMessage("Encoding cancelled: Key not saved.", 5000)
            return

        try:
            fernet = Fernet(key.encode())
            encrypted_bytes = fernet.encrypt(current_text.encode())
            encrypted_text = encrypted_bytes.decode()

            self.editor.setPlainText(encrypted_text)
            self.lock_editor()
            self.status_bar.showMessage("Content encoded successfully.", 4000)
            # Optionally, save this encrypted content automatically or prompt the user
            # For now, we just replace the text in the editor

        except Exception as e:
            QMessageBox.critical(self, "Encoding Error", f"Failed to encode content:\n{e}")
            self.status_bar.showMessage("Encoding failed.", 5000)

    def decode_content_dialog(self):
        encrypted_text = self.editor.toPlainText()
        if not encrypted_text.strip():
            QMessageBox.warning(self, "Empty Content", "The editor is empty. Nothing to decode.")
            return

        # Ask for the key
        key_input, ok = QInputDialog.getText(self, "Decode Content", "Enter the encryption key:")

        if ok and key_input:
            try:
                fernet = Fernet(key_input.encode())
                decrypted_bytes = fernet.decrypt(encrypted_text.encode())
                decrypted_text = decrypted_bytes.decode()

                self.editor.setPlainText(decrypted_text)
                self.unlock_editor()
                self.status_bar.showMessage("Content decoded successfully.", 4000)

            except InvalidToken:
                QMessageBox.critical(self, "Decoding Error", "Invalid key or corrupted data. Decoding failed.")
                self.status_bar.showMessage("Decoding failed: Invalid key.", 5000)
            except Exception as e:
                QMessageBox.critical(self, "Decoding Error", f"An unexpected error occurred during decoding:\n{e}")
                self.status_bar.showMessage("Decoding failed.", 5000)
        else:
            self.status_bar.showMessage("Decoding cancelled.", 3000)

    def create_encrypted_backup(self, file_path: str):
        try:
            with open(file_path, "rb") as f:
                original_data = f.read()

            # Generate a key FOR BACKUP - this key is NOT shown to the user
            # and is only used for this specific backup file.
            # You might want to use a more persistent key derivation if you need to access backups later.
            backup_key = Fernet.generate_key()
            fernet_backup = Fernet(backup_key)
            encrypted_data = fernet_backup.encrypt(original_data)

            # Define backup filename
            base_name = Path(file_path).stem
            timestamp = int(time.time())
            backup_filename = f"{base_name}_{timestamp}.enc"
            backup_path = os.path.join(self.app_data_local, backup_filename)

            with open(backup_path, "wb") as f:
                f.write(encrypted_data)

            # Note: The backup_key itself is ephemeral here. If you need to ACCESS backups later,
            # you'll need a strategy to store/retrieve these backup keys securely.
            # For now, it just creates an encrypted file.
            print(f"Encrypted backup created at: {backup_path}") # For debugging

        except Exception as e:
            print(f"Error creating encrypted backup: {e}") # Log or show error to user if critical

    def lock_editor(self):
        self.editor.setReadOnly(True)
        self.editor_locked = True
        self.status_bar.showMessage("Editor locked.", 3000)

    def unlock_editor(self):
        self.editor.setReadOnly(False)
        self.editor_locked = False
        self.status_bar.showMessage("Editor unlocked.", 3000)

    def toggle_editor_lock(self):
        if self.editor_locked:
            self.unlock_editor()
        else:
            self.lock_editor()

    def show_about_dialog(self):
        dialog = AboutDialog(self.about_text, self)
        dialog.exec()


def main():
    app = QApplication(sys.argv)
    app.setApplicationName(APP_TITLE)

    window = VortMainWindow()
    window.show()

    if len(sys.argv) > 1:
        incoming_path = sys.argv[1]
        if os.path.isfile(incoming_path):
            window.open_vort_file_direct(incoming_path)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
