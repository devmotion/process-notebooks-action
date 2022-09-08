FROM python:3.10-alpine
COPY requirements.txt generate_public.py /root/
RUN python -m pip install --upgrade pip && python -m pip install -r /root/requirements.txt
ENTRYPOINT ["python", "/root/generate_public.py"]
CMD ["--help"]
