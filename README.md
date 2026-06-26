# LICTOR

```text
LICTOR // LOCAL INDICATOR AND CASE TRIAGE OPERATOR
```

**LICTOR** is the harder brother of **CIVITAS**.

Where CIVITAS structures cases and evidence, LICTOR interrogates indicators before they become a case.

Developed solely by **xtr4ng3**.

---

## Interface

LICTOR now ships with the **Obsidian interface**: a heavier dark console aesthetic with structured telemetry, signal lanes, inline result rendering and a stronger operational identity, while still using only the Python standard library.

## Purpose

LICTOR is a local-first defensive triage engine for:

- suspicious URLs;
- suspicious domains;
- email senders and bodies;
- scam-pressure text patterns;
- local files and hashes.

It does not perform network lookups.  
It does not send hidden messages.  
It does not collect credentials.  
It does not upload data.

---

## Position in the OXLGR ecosystem

```text
FARO      -> protects families during suspicious interactions
LICTOR    -> interrogates indicators and marks risk signals
CIVITAS   -> structures evidence and case material
EIDOLON   -> manages forensic case work
RAVENLOCK -> monitors integrity and drift
LABYRINTH -> generates defensive laboratories
```

---

## Why the name

A lictor was an executor of civic authority.  
In this project, LICTOR acts as the cold officer between raw suspicion and structured evidence.

```text
CIVITAS = the city, the record, the case.
LICTOR  = the blade at the gate.
```

---

## Features

### URL / Domain

LICTOR flags local static signals:

- HTTP;
- shorteners;
- punycode;
- raw IP host;
- too many subdomains;
- many hyphens;
- suspicious words;
- possible brand resemblance;
- sensitive query parameters.

### Email

LICTOR reviews:

- sender domain;
- free email impersonation;
- claimed entity;
- subject;
- body;
- embedded links;
- urgency;
- code/password/token requests;
- institution-like sensitive requests.

### Text

LICTOR detects:

- requests for code, token, PIN, password or key;
- urgent pressure;
- money transfer language;
- secrecy requests;
- remote-access attempts;
- changed-number / family emergency phrasing.

### File

LICTOR calculates:

- MD5;
- SHA1;
- SHA256.

It also flags risky executable/script-like extensions.

---

## GUI

Run:

```bash
python lictor.py gui
```

Or double-click:

```text
ABRIR_LICTOR.bat
```

If no command is provided, LICTOR attempts to open the GUI.

---

## CLI

### Initialize

```bash
python lictor.py init
```

JSON:

```bash
python lictor.py init --json --pretty
```

### URL

```bash
python lictor.py url "http://bit.ly/test?token=1"
```

```bash
python lictor.py url "http://bit.ly/test?token=1" --json --pretty
```

### Domain

```bash
python lictor.py domain "example.com" --json --pretty
```

### Email

```bash
python lictor.py email --sender "support@hotmail.com" --claimed "Microsoft" --subject "Cuenta bloqueada" --body "Tu cuenta será cerrada. Confirma tu clave." --json --pretty
```

### Text

```bash
python lictor.py text "Soy tu nieto, cambié de número. Necesito plata urgente, no le digas a nadie." --json --pretty
```

### File

```bash
python lictor.py file "sample.exe" --json --pretty
```

### History

```bash
python lictor.py history
```

```bash
python lictor.py history --json
```

```bash
python lictor.py history --csv exports/history.csv
```

---

## Stable JSON

All main scan commands support:

```text
--json
--pretty
--out
--save
--html
```

Base structure:

```json
{
  "id": "...",
  "created_at": "...",
  "tool": "LICTOR",
  "version": "1.0.0",
  "author": "xtr4ng3",
  "type": "url",
  "input": "...",
  "score": 70,
  "level": "HIGH",
  "recommendation": "...",
  "signals": []
}
```

---

## Local Data

Local history:

```text
lictor_data/lictor.sqlite3
```

Reports:

```text
lictor_data/reports/
```

Exports:

```text
lictor_data/exports/
```

---

## Windows Scripts

```text
ABRIR_LICTOR.bat       -> open GUI
VALIDAR_LICTOR.bat     -> run syntax checks and tests
CREAR_EXE_OPCIONAL.bat -> optional PyInstaller build
```

---

## Security

```text
NO SPYWARE
NO CREDENTIAL THEFT
NO HIDDEN SENDING
NO COVERT UPLOAD
NO UNAUTHORIZED ACCESS
NO DESTRUCTIVE AUTOMATION
```

---

## Author

```text
xtr4ng3
```

```text
LICTOR // Local Indicator and Case Triage Operator
```

---

## License

MIT.
