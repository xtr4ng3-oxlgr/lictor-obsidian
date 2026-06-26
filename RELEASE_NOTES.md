# LICTOR v1.0.0

Initial public release.

## Identity

LICTOR replaces the old ARGUS/VIGIL concept with a harder, cleaner tool identity aligned with CIVITAS.

```text
CIVITAS = the city, the record, the case.
LICTOR  = the blade at the gate.
```

## Highlights

- Stable CLI.
- GUI optional.
- JSON support tested.
- Local SQLite history.
- HTML reports.
- CSV export.
- URL/domain/email/text/file triage.
- File hashes: MD5, SHA1, SHA256.
- No external dependencies.
- No network calls.
- No hidden sending.

## Tested

```text
python lictor.py init --json
python lictor.py url "http://bit.ly/a?token=1" --json
python lictor.py email --sender "support@hotmail.com" --claimed "Microsoft" --subject "Cuenta bloqueada" --body "Confirma tu clave urgente" --json
python lictor.py text "Soy tu nieto cambié de número necesito plata urgente no le digas a nadie" --json
python tests/test_lictor.py
```


## Interface refresh

- New Obsidian GUI with darker operational styling.
- Enhanced telemetry panel with score gauge, signals lane and structured output panel.
- Stronger CIVITAS/LICTOR sibling identity.
