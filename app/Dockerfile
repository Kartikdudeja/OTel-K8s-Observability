# lightweight base image
FROM python:3.10.12-slim

# metadata
LABEL app="ml-prediction-model"
LABEL env="dev"
LABEL lab="observability"

# create a non-root user and group
RUN adduser --disabled-password --gecos '' appuser

# set working directory for application
WORKDIR /app

# copy list of required dependencies
COPY requirements.txt .

# install dependencies as root
RUN pip install --no-cache-dir -r requirements.txt

# cleanup dockerfile
RUN rm -rf /tmp/*

# add application code and ml model
COPY app.py .
COPY house_price_model.pkl .

# Change ownership to the non-root user
RUN chown -R appuser:appuser /app

# Switch to the non-root user
USER appuser

# export port for application listener and otlp
EXPOSE 8000
EXPOSE 4317

# start application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
