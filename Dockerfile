FROM python:3.9.18-alpine3.19 as builder
WORKDIR /music-audiolyser
COPY ["pyproject.toml", "Makefile", "requirements.txt"]
RUN make install-docker

FROM tensorflow/tensorflow:latest-gpu
COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
COPY ./src/ /music-audiolyser
CMD ["python"]