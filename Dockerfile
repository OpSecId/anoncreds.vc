FROM python:3.12

WORKDIR /flask

ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY pyproject.toml ./

RUN pip install poetry
RUN poetry install

COPY app ./app
COPY config.py main.py ./

# CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "main:app"]
CMD [ "python", "main.py" ]