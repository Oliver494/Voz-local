# Instalación de Voz Local

Esta guía también está en la web, en **Instalación**. Puedes leer este archivo antes de instalar el servidor.

## Disponibilidad actual

| Sistema | Estado de este proyecto |
| --- | --- |
| Linux | `bash instalar-e-iniciar.sh`. Instala dependencias con apt, dnf o pacman. |
| Windows | Doble clic en `Instalar e iniciar.bat`. FFmpeg se instala con WinGet. |
| Mac Apple Silicon | Abre `Instalar e iniciar.command` o ejecuta `bash instalar-e-iniciar.sh`. |

Los iniciadores están preparados, pero la instalación completa en Windows y macOS todavía no se ha probado en equipos reales. No se garantiza soporte para cualquier GPU o distribución. El instalador no cambia controladores del sistema ni instala Ollama. Python se prepara mediante [uv](https://docs.astral.sh/uv/guides/install-python/) en un entorno propio del proyecto, aunque no exista Python en el equipo.

JavaScript, HTML y CSS funcionan en el navegador. No necesitas instalar Node.js, Java ni un compilador de frontend.

## Linux

Descarga y extrae el proyecto. Abre una terminal dentro de su carpeta. No copies el entorno `.venv` de otro equipo: hay que crearlo en el equipo de destino.

```bash
bash instalar-e-iniciar.sh
```

El iniciador instala FFmpeg y las herramientas de descarga si faltan, utilizando apt, dnf o pacman. Puede pedir la contraseña del sistema. En otras distribuciones, indicará qué falta instalar.

Prepara Python 3.12, un entorno `.venv`, PyTorch y las bibliotecas del proyecto; descarga Qwen3-TTS 1.7B y abre el navegador cuando el servidor responde. Reutiliza un entorno ya funcional en este PC. Selecciona la compilación ROCm existente para `gfx1200` si detecta RX 9060 XT; CUDA para NVIDIA con controlador; o CPU en otros casos. No instala controladores AMD/NVIDIA.

## Windows

Haz doble clic en **Instalar e iniciar.bat** dentro de la carpeta extraída completa. Necesita la carpeta `scripts`; descargar solo el `.bat` no basta. El iniciador está dirigido a Windows x64 (no Windows de 32 bits ni ARM).

1. Descarga uv desde su fuente oficial si falta.
2. Instala FFmpeg mediante `winget install --id Gyan.FFmpeg --exact --source winget` si no lo encuentra. Los permisos y las licencias los acepta la persona que ejecuta el instalador.
   También prepara Microsoft Visual C++ Redistributable x64 si falta, para las bibliotecas de PyTorch.
3. Descarga Python 3.12 si falta, sin reemplazar otros Python del sistema.
4. Crea el entorno, instala bibliotecas, descarga el modelo e inicia la web.

Si no tienes [WinGet](https://learn.microsoft.com/windows/package-manager/winget/), instala **App Installer** de Microsoft y vuelve a abrir el archivo. Después de instalar FFmpeg puede ser necesario cerrar y reabrir el `.bat` para actualizar el PATH.

La compilación seleccionada usa CUDA si detecta `nvidia-smi`. Sin NVIDIA, utiliza CPU; las GPU AMD en Windows no se configuran automáticamente. Los controladores y la GPU deben ser compatibles con la compilación CUDA instalada. El `.bat` usa una política de ejecución de PowerShell solo para ese proceso; no modifica permanentemente la política del equipo.

## macOS — Apple Silicon

Abre **Instalar e iniciar.command**. Si no se abre, utiliza una terminal en la carpeta del proyecto:

```bash
bash instalar-e-iniciar.sh
```

Instala Homebrew desde su fuente oficial si falta y se necesita FFmpeg. Homebrew puede pedir permisos o herramientas del sistema. Después instala FFmpeg, prepara Python, bibliotecas y modelo, e inicia la web.

El modo predeterminado es CPU. [MPS](https://docs.pytorch.org/docs/stable/notes/mps.html) queda como opción experimental con `VOZ_LOCAL_DEVICE=mps`; no se ha comprobado la generación en un Mac real. Este instalador no admite Macs Intel.

## Próximos inicios y archivos para distribuir

La sección **Instalación** ofrece **Descargar proyecto ZIP**. El paquete contiene el código y los iniciadores, sin tus voces, proyectos, entornos ni modelos descargados. En el equipo de destino, extrae todo el ZIP antes de abrir el iniciador. Para reconstruir el paquete después de cambiar el código, ejecuta `python scripts/package.py` con un Python disponible.

Abre el mismo iniciador otra vez. Reutiliza las bibliotecas y los modelos ya preparados; no descarga el modelo si los archivos necesarios están presentes. Mantén su ventana abierta durante el uso. Pulsa Ctrl+C para apagar el servidor.

Distribuye el código, `static/`, `app/`, `scripts/`, `requirements.txt` y los iniciadores. Excluye `.venv/`, `.installer/`, `.runtime/` y `data/`: contienen entornos específicos del equipo y tus voces, proyectos y audios personales. La instalación crea las carpetas necesarias.

## Ollama e internet

Ollama es opcional: solo ayuda a editar los guiones. La clonación utiliza Qwen3-TTS directamente. Puedes descargar Ollama desde su [página oficial](https://ollama.com/download).

Necesitas internet para instalar las dependencias y descargar cada modelo por primera vez. Después, la generación es local. Elegir un modelo que no está descargado puede iniciar una descarga.

Los perfiles, modelos y proyectos se guardan en `data/`. Conserva esta carpeta para mantener tus trabajos. Un enlace localhost por sí solo no instala ni inicia la aplicación.

Consulta también la [documentación oficial de Qwen3-TTS](https://github.com/QwenLM/Qwen3-TTS).
