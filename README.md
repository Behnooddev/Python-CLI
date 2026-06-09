# VORT Editor

VORT Editor is a modern Python-based application for creating, editing, validating, and encrypting custom `.vort` files.

Designed with a hacker-inspired interface and focused on secure local file management.

---

## ✨ Features

* 🔐 Encode / Decode system using Fernet encryption
* 📄 Custom `.vort` file structure
* 🧠 SHA256 integrity validation
* 💬 Real-time text editing
* 🟢 Hacker-style dark interface
* 📁 File save/open support
* 🔒 Editor lock system
* 💾 Automatic encrypted backups
* 🖱️ Windows Registry integration
* 📦 Windows release build included
* 📂 Right-click → New → VORT file support

---

## 🛠️ Built With

* Python 🐍
* PySide6
* Cryptography (Fernet)

---

## 📂 Project Structure

```txt
VoidRoot/
│
├── CLI.py
├── requirements.txt
├── README.md
├── LICENSE
├── release/
├── registry/
└── assets/
```

---

## 📸 Screenshot

Add your application screenshot inside:

```txt
/assets/screenshot.png
```

Then use:

```md
![Screenshot](assets/screenshot.png)
```

---

## ⚡ Installation

Clone the repository:

```bash
git clone https://github.com/Behnooddev/voidroot-editor.git
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the application:

```bash
python CLI.py
```

---

## 🔐 About VORT Files

`.vort` files contain a custom structure including:

* SHA256 integrity validation
* Random salt generation
* Base64 payload encoding

The editor also supports encrypted content using Fernet symmetric encryption.

---

## 🖥️ Windows Integration

The project includes:

* Windows Registry integration
* Custom `.vort` file association
* Right-click creation support
* Standalone Windows release build

---

## ⚠️ Disclaimer

This software is provided for educational and personal use.

The developer, **Behnood Shafiei**, is not responsible for:

* misuse of the software
* data loss
* damages
* security issues
* legal problems caused by user actions

Users are fully responsible for how they use this software.

---

## 👨‍💻 Developer

Developed by **Behnood Shafiei**

Cybersecurity, networking, and backend development enthusiast.

---

## 📜 License

You are allowed to use, modify, and share this project with proper credit to the original developer:

**Behnood Shafiei**

Removing author credits or claiming the project as your own is not permitted.
