FROM python:3.9

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./app /code/app

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser
RUN chown -R appuser:appuser /code
USER appuser

# Use port 8000 instead of 80 (non-privileged port)
CMD ["fastapi", "run", "app/main.py", "--port", "8000", "--host", "0.0.0.0"]
