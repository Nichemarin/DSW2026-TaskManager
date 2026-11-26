# Usamos una imagen oficial de Python ligera
FROM python:3.14-slim

# Instalar sudo (requerido por VS Code Dev Containers para ajustar el UID dinámicamente)
RUN apt-get update && apt-get install -y sudo && rm -rf /var/lib/apt/lists/*

# Crear el usuario vscode con UID 1000 y darle permisos de sudo sin contraseña
RUN useradd -m -s /bin/bash -u 1000 vscode \
    && echo "vscode ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# Instalamos uv copiando directamente sus binarios oficiales
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Cambiar la propiedad de la carpeta de trabajo antes de copiar archivos
RUN chown -R vscode:vscode /app

# Cambiamos al usuario vscode para las siguientes instrucciones
USER vscode

# 1. Copiamos nuestro archivo de dependencias al contenedor
COPY --chown=vscode:vscode pyproject.toml .

# 2. Sincronizamos el proyecto: uv creará .venv y descargará FastAPI y Uvicorn
RUN uv sync

# Exponemos el puerto 8000 (puerto estándar de Uvicorn / FastAPI)
EXPOSE 8000

# 3. Ejecutamos nuestra API usando 'uv run fastapi run'
CMD ["uv", "run", "fastapi", "run", "app/main.py", "--host", "0.0.0.0", "--port", "8000"]