FROM python:alpine3.7
COPY . /root/
RUN pip install --upgrade pip \
    && pip install -r /root/requirements.txt
ENTRYPOINT ["python", "/root/generate_public.py"]
CMD ["--help"]