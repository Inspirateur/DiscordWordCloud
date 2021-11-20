FROM python:3.9-slim as base
WORKDIR /app

FROM base as requirements

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# doing this instead of using requirements.txt was WAY faster
RUN python -m pip install --disable-pip-version-check discord
RUN python -m pip install --disable-pip-version-check numpy
RUN python -m pip install --disable-pip-version-check wordcloud
RUN python -m pip install --disable-pip-version-check async_lru
RUN python -m pip install --disable-pip-version-check aiohttp
RUN python -m pip install --disable-pip-version-check emoji
RUN python -m pip install --disable-pip-version-check Pillow
RUN python -m pip install --disable-pip-version-check tqdm
RUN python -m pip install --disable-pip-version-check colorama

FROM requirements as files
COPY . ./

FROM files as dowork
CMD ["python", "main.py"]