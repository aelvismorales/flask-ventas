# Usa una imagen base de Python
FROM python:3.12

# Establece el directorio de trabajo en la carpeta de la aplicación
WORKDIR /app

# Copia los archivos de requerimientos al contenedor
COPY requirements.txt ./

# Instala las dependencias
RUN pip install -r requirements.txt

# Copia los archivos de la aplicación al contenedor
COPY . .

COPY .env .env
# Expone el puerto 5000 (el puerto en el que Flask suele ejecutarse)
EXPOSE 5000

# Comando para ejecutar la aplicación Flask
CMD ["python", "run.py"]