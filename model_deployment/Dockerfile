FROM ultralytics/ultralytics:latest-jetson-jetpack6

RUN pip install --no-cache-dir streamlit==1.37.0

WORKDIR /app

COPY app.py /app/app.py
COPY test.mp4 /videos/test.mp4

EXPOSE 8501

ENTRYPOINT ["streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=8501"]