# SPDX-FileCopyrightText: 2024-2025 Damian Fajfer <damian@fajfer.org>
#
# SPDX-License-Identifier: EUPL-1.2
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN useradd -m -u 1000 perplexity && chown -R perplexity:perplexity /app
USER perplexity

CMD ["python", "main.py"]