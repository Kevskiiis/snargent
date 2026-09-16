FROM node:22-bookworm

WORKDIR /workspace

RUN apt-get update \
	&& apt-get install -y --no-install-recommends make git ca-certificates \
	&& rm -rf /var/lib/apt/lists/* \
	&& npm install -g npm@latest