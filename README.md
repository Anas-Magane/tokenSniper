# TokenSniper – AI Powered JWT Tool

**By [Anas Education](https://www.youtube.com/@Anas_Education)** | [LinkedIn](https://www.linkedin.com/in/anas-magane-3aa287262/) | [GitHub](https://github.com/Anas-Magane)

TokenSniper is a powerful and educational CLI tool for analyzing, decoding, and brute-forcing JWT tokens — enhanced with optional AI integration (Groq + LLaMA).

---

## Features

- Detect token type (JWT, UUID, HEX...)
- Decode JWT tokens (Base64 decode + JSON pretty print)
- Encode JWT (manual or via AI prompts)
- Brute-force JWT secrets (multithreaded)
- Exploit “None Algorithm” trick
- Change JWT algorithm
- AI Suggestions: Analyze structure, security, usage & attack vectors

---

## Setup Instructions

### 1. Clone the repo

```bash
git clone https://github.com/Anas-Magane/tokenSniper.git
cd tokenSniper
```

### 2. Install requirements

```bash
pip install -r requirements.txt
```

### 3. Create `.env` with your Groq API Key

```bash
cp .env.example .env
nano .env
```

Example:

```env
GROQ_API_KEY=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
```

> This key is safe and ignored by Git using `.gitignore`.

---

### 4. Run the tool

```bash
python3 tokenSniper.py
```

---

## Author & Links

Made by **Anas Magane**  
[LinkedIn](https://www.linkedin.com/in/anas-magane-3aa287262/)  
[YouTube - Anas Education](https://www.youtube.com/@Anas_Education)  
[GitHub](https://github.com/Anas-Magane)

---

## License

MIT License
