FROM python:alpine3.7
COPY . /app
WORKDIR /app
RUN pip install --upgrade pip \
    && pip install -r requirements.txt
ENTRYPOINT ["python", "./generate_public.py"]
CMD ["--help"]