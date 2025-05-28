#base image inside our github container registry for repo github.com/beusefulai/inboard
FROM ghcr.io/br3ndonland/inboard:fastapi-python3.10-slim

# Set environment variables
ENV HATCH_ENV_TYPE_VIRTUAL_PATH=.venv
ENV SERVER_NAME=${DOMAIN}
ENV SERVER_HOST=https://${DOMAIN}
ENV SMTP_HOST=${SMTP_HOST}

# Copy application code
COPY ./app/ /app/
WORKDIR /app/

# Install dependencies
RUN hatch env prune && \
    hatch env create production && \
    pip install --upgrade setuptools

# Optional Jupyter installation
ARG INSTALL_JUPYTER=false
RUN bash -c "if [ $INSTALL_JUPYTER == 'true' ] ; then pip install jupyterlab ; fi"

# Set backend configuration
ARG BACKEND_APP_MODULE=app.main:app
ARG BACKEND_PRE_START_PATH=/app/prestart.sh
ARG BACKEND_PROCESS_MANAGER=gunicorn
ARG BACKEND_WITH_RELOAD=false
ENV APP_MODULE=${BACKEND_APP_MODULE} \
    PRE_START_PATH=${BACKEND_PRE_START_PATH} \
    PROCESS_MANAGER=${BACKEND_PROCESS_MANAGER} \
    WITH_RELOAD=${BACKEND_WITH_RELOAD}

# Configure logging
ENV LOGGING_DRIVER=json-file
ENV LOGGING_MAX_SIZE=200k
ENV LOGGING_MAX_FILE=3

# Workers
ENV MAX_WORKERS=5

# The inboard image likely has an ENTRYPOINT or CMD already defined
# If you need to override it, you can add:
# CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "-c", "/gunicorn_conf.py", "app.main:app"]