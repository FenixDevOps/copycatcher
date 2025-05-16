# Copy Catcher 📝

Detect plagiarism with style! Copy Catcher scans text or files for similarities. It’s fast, vibrant, and easy to use.

## ✨ Features

- **Plagiarism Check**: Spots matches from 1% to 100%. 🎯
- **Cool UI**: Colorful gradients. Animated results. Aligned buttons. 🌈
- **File Support**: Upload .txt, .docx, .pdf. 📄
- **No Reloads**: Smooth, async experience. ⚡
- **Database**: Saves results in SQLite. 💾
- **API Ready**: Test with Postman. 🛠️

## 🛠️ Setup

1. **Clone Repo**:

   ```bash
   git clone https://github.com/<your-username>/Copy-Catcher.git
   cd Copy-Catcher
   ```

2. **Virtual Env**:

   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   pip install -r requirements.txt
   python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
   ```

3. **Uploads Folder**:

   ```bash
   mkdir Uploads
   ```

## 🚀 Run It

1. **Backend**:

   ```bash
   python app.py
   ```

   See: `http://127.0.0.1:5000`

2. **Frontend**:

   ```bash
   python -m http.server 5500
   ```

   Open: `http://localhost:5500`

## 📋 Use It

- **Paste Text**: Enter text. Click "Analyze Text". See results. ✅
- **Upload File**: Add .txt/.docx/.pdf. Click "Analyze File". Done! 📥
- **API Test**: POST to `/upload-text` or `/upload-file`. Use Postman. 🔌

## 🧪 Test Case

**100% Plagiarized**:

```
Python is a high-level programming language designed to be easy to read and simple to implement.
```

**Result**:

- Similarity: 100%
- Message: "Warning: Plagiarism detected!"
- Duplicate: "Online Source 1"

## 🐛 Issues?

- **Port Clash**: Kill port 5000: `taskkill /PID <pid> /F`.
- **Setup Fail**: Reinstall: `pip install -r requirements.txt`.
- **UI Oddity**: Clear cache (Ctrl+Shift+R).

## 🤝 Contribute

Fork it. Code it. PR it. Let’s build! 🚀

## 📜 License

MIT License. See LICENSE.

## 📬 Contact

- **Author**: B. Manikanta
- **GitHub**:https://github.com/FenixDevOps
- **email**: manigoud8885@gmail.com
