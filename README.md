# LICTOR

```text
LICTOR // OPERADOR LOCAL DE TRIAGE DE INDICADORES Y CASOS
```

**LICTOR** es una herramienta local de análisis preliminar para indicadores sospechosos, presión digital, correos, enlaces, dominios, textos y archivos.

Desarrollado únicamente por **xtr4ng3**.

---

## Identidad operativa

```text
CIVITAS = estructura, archivo, caso.
LICTOR  = umbral, interrogación, señal.
```

Dentro del ecosistema OXLGR, LICTOR funciona como una unidad complementaria de **CIVITAS**.

**CIVITAS** ordena evidencia, casos e inteligencia práctica.  
**LICTOR** revisa indicadores antes de que una sospecha se convierta en expediente.

```text
LICTOR -> brazo ejecutor de CIVITAS: triage de indicadores, presión y umbral de caso.
```

---

## Propósito

LICTOR está orientado a revisión defensiva y local de:

- URLs sospechosas;
- dominios sospechosos;
- remitentes y cuerpos de correo;
- textos con presión de estafa o ingeniería social;
- archivos locales y hashes.

No realiza búsquedas en red.  
No envía mensajes ocultos.  
No recolecta credenciales.  
No sube datos.  
No ejecuta acciones destructivas.

---

## Interfaz Obsidian

LICTOR incluye una interfaz gráfica oscura, pesada y operativa, diseñada como consola de triage local.

La interfaz muestra:

- panel lateral de módulos;
- revisión de URL / dominio;
- revisión de correos;
- revisión de texto;
- revisión de archivos;
- historial local;
- barra visual de riesgo;
- señales detectadas;
- salida JSON estructurada;
- exportación de reportes.

La interfaz mantiene el mismo principio del motor principal:

```text
todo local
todo visible
todo revisable
```

---

## Posición dentro de OXLGR

```text
F.A.R.O.        -> orden forense local
CIVITAS         -> estructura cívica de casos e inteligencia práctica
LICTOR          -> brazo ejecutor de CIVITAS: triage de indicadores, presión y umbral de caso
EIDOLON         -> identidad, rastro y residuo digital
WARDEN-11       -> patrulla de superficie, señales y postura
RAVENLOCK v2    -> capa sellada de utilidad
BLACKLAMP       -> limpieza e inspección controlada
OXLGR Sentinel  -> observación de procesos y endpoint
SHADOWLINK      -> flujo lateral de terminal
COLDCASE        -> manejo de casos forenses
NERVECHECK      -> diagnóstico para usuario común
```

---

## Funciones principales

### URL / dominio

LICTOR marca señales locales como:

- uso de HTTP;
- acortadores;
- punycode;
- host por IP directa;
- exceso de subdominios;
- exceso de guiones;
- palabras sensibles;
- semejanza con marcas conocidas;
- parámetros sensibles en la consulta.

### Correo

LICTOR revisa:

- remitente;
- dominio del remitente;
- entidad declarada;
- asunto;
- cuerpo;
- enlaces incrustados;
- urgencia;
- pedidos de códigos, claves, token o PIN;
- intentos de suplantación institucional.

### Texto

LICTOR detecta patrones de presión como:

- pedido de código, token, PIN, clave o contraseña;
- urgencia artificial;
- pedidos de transferencia o dinero;
- aislamiento o secreto;
- acceso remoto;
- cambio de número;
- emergencia familiar;
- lenguaje típico de manipulación.

### Archivo

LICTOR calcula:

- MD5;
- SHA1;
- SHA256.

También marca extensiones ejecutables o de script que requieren revisión cuidadosa.

---

## Uso gráfico

En Windows, abrir:

```text
ABRIR_LICTOR.bat
```

También puede ejecutarse desde terminal:

```bash
python lictor.py gui
```

Si no se indica ningún comando, LICTOR intenta iniciar la interfaz gráfica.

---

## Uso por consola

### Inicializar

```bash
python lictor.py init
```

Con salida JSON:

```bash
python lictor.py init --json --pretty
```

### Analizar URL

```bash
python lictor.py url "http://bit.ly/test?token=1"
```

Con salida JSON:

```bash
python lictor.py url "http://bit.ly/test?token=1" --json --pretty
```

### Analizar dominio

```bash
python lictor.py domain "example.com" --json --pretty
```

### Analizar correo

```bash
python lictor.py email --sender "support@hotmail.com" --claimed "Microsoft" --subject "Cuenta bloqueada" --body "Tu cuenta será cerrada. Confirma tu clave." --json --pretty
```

### Analizar texto

```bash
python lictor.py text "Soy tu nieto, cambié de número. Necesito plata urgente, no le digas a nadie." --json --pretty
```

### Analizar archivo

```bash
python lictor.py file "sample.exe" --json --pretty
```

### Ver historial

```bash
python lictor.py history
```

Historial en JSON:

```bash
python lictor.py history --json
```

Exportar historial CSV:

```bash
python lictor.py history --csv exports/history.csv
```

---

## Salida JSON

Los comandos principales aceptan:

```text
--json
--pretty
--out
--save
--html
```

Estructura base:

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

## Datos locales

Historial local:

```text
lictor_data/lictor.sqlite3
```

Reportes:

```text
lictor_data/reports/
```

Exportaciones:

```text
lictor_data/exports/
```

---

## Scripts de Windows

```text
ABRIR_LICTOR.bat           -> abre la interfaz gráfica
VALIDAR_LICTOR.bat         -> ejecuta validaciones y pruebas
CREAR_EXE_OPCIONAL.bat     -> crea ejecutable de consola con PyInstaller
CREAR_EXE_GUI_OPCIONAL.bat -> crea ejecutable gráfico con PyInstaller
```

---

## Seguridad

```text
SIN SPYWARE
SIN ROBO DE CREDENCIALES
SIN ENVÍO OCULTO
SIN SUBIDA ENCUBIERTA
SIN ACCESO NO AUTORIZADO
SIN AUTOMATIZACIÓN DESTRUCTIVA
```

LICTOR está diseñado para uso defensivo, local y autorizado.

---

## Autor

```text
xtr4ng3
```

```text
LICTOR // Operador Local de Triage de Indicadores y Casos
```

---

## Licencia

<img width="300" height="159" alt="giphy (25)" src="https://github.com/user-attachments/assets/021720ff-3aec-4916-9a93-25d47afd7d97" />

**xtr4ng3**

MIT.
