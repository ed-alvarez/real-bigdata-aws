# Real Big Data - Amazon Web Services

This project is designed to collect, store and process data from various
communication platforms. The collected data can be
used for compliance monitoring, sentiment analysis, security auditing, or business intelligence.

## Platforms

- Slack, Teams, and Zoom
- WhatsApp
- VoIP (SIP)
- Email accounts

## How it works

1. Ingestion Layer

Each module runs individually in its own lambda container temporarily and rotating
accordingly to usage.

2. Processing Layer

Like the Ingestion Layer, the Processing Layer is designed to automatically
process and make sure only the required information is sent through and in JSON
format.

3. Storage & Analysis

The processed data is stored in the specific data lakes using the following
technology:

- Kafka
- AWS S3
- Elasticsearch
