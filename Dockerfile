FROM python:3

# Define variables de entorno
ENV PYTHONUNBUFFERED 1

# Establece el directorio de trabajo
WORKDIR /code

# Instala las dependencias
COPY requirements.txt /code/
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto de los archivos del proyecto
COPY . /code/

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "myproject.wsgi:application"]
