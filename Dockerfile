FROM python:3.7-slim

RUN mkdir -p /app
COPY . stockAdvisor.py /app/
WORKDIR /app
RUN pip install -r requirements.txt
EXPOSE 8080
CMD [ "stockAdvisor.py" ]]
ENTRYPOINT [ "python" ]