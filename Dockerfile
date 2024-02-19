FROM registry.access.redhat.com/ubi9/python-39:latest

# This will avoid people forgetting to set no-cache-dir when building images
ENV PIP_NO_CACHE_DIR=1

USER 0

COPY app.py utils.py requirements.txt ./
ADD models models

# Install packages and cleanup
# (all commands are chained to minimize layer size)
RUN echo "Installing softwares and packages" && \
    pip install -r requirements.txt && \
    chmod -R g+w /opt/app-root/lib/python3.9/site-packages && \
    fix-permissions /opt/app-root -P 

USER 1001

CMD [ "python", "app.py"]