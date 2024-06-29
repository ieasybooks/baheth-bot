FROM --platform=linux/amd64 mcr.microsoft.com/vscode/devcontainers/base:ubuntu-24.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
    && apt-get install -y gnupg curl wget unzip --no-install-recommends \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | gpg --no-default-keyring --keyring gnupg-ring:/etc/apt/trusted.gpg.d/google.gpg --import \
    && chmod 644 /etc/apt/trusted.gpg.d/google.gpg \
    && echo "deb [arch=amd64] https://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN CHROMEDRIVER_VERSION=$(curl https://googlechromelabs.github.io/chrome-for-testing/LATEST_RELEASE_STABLE) \
    && wget -N https://storage.googleapis.com/chrome-for-testing-public/$CHROMEDRIVER_VERSION/linux64/chromedriver-linux64.zip -P ~/ \
    && unzip ~/chromedriver-linux64.zip -d ~/ \
    && rm ~/chromedriver-linux64.zip \
    && mv -f ~/chromedriver-linux64/chromedriver /usr/bin/chromedriver \
    && rm -rf ~/chromedriver-linux64 \
    && chmod +x /usr/bin/chromedriver
