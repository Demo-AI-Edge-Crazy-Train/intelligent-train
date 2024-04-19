FROM nvcr.io/nvidia/l4t-jetpack:r36.2.0

# This will avoid people forgetting to set no-cache-dir when building images
ENV PIP_NO_CACHE_DIR=1

USER 0

COPY src/app.py src/utils.py src/requirements.txt ./
ADD models models

RUN apt update && apt install -y git python3-pip && \
    wget https://nvidia.box.com/shared/static/i7n40ki3pl2x57vyn4u7e9asyiqlnl7n.whl -O onnxruntime_gpu-1.16.0-cp310-cp310-linux_aarch64.whl && \
    pip3 install onnxruntime_gpu-1.16.0-cp310-cp310-linux_aarch64.whl && \
    pip3 install -r requirements.txt

CMD [ "python3", "app.py"]
