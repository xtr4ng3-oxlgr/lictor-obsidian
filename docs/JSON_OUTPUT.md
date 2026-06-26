# LICTOR JSON Output

Every scan command returns the same base structure.

```json
{
  "id": "uuid",
  "created_at": "iso timestamp",
  "tool": "LICTOR",
  "version": "1.0.0",
  "author": "xtr4ng3",
  "type": "url | email | text | file | init",
  "input": "original input",
  "score": 0,
  "level": "INFO | LOW | MEDIUM | HIGH | CRITICAL",
  "color": "#hex",
  "recommendation": "human recommendation",
  "signals": [
    {
      "code": "signal_code",
      "weight": 10,
      "detail": "signal description"
    }
  ]
}
```

Supported on scan commands:

```text
--json
--pretty
--out
--save
--html
```
