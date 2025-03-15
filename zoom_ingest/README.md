<!--
title: 'Zoom ingest agents'
description: 'Zoom INgest Agents for Fingerprint Supervision.'
layout: Doc
framework: v3
platform: AWS
language: python
priority: 2
authorLink: 'https://github.com/ip-sentinel'
authorName: 'James Hogbin'
-->


# Zoom ingest Agents (for Melqart)

Zoom agents to ingest CDR & Transcripts from Zoom for Meetings and Calls
Also download audio tracks for archival

## Overview

* Will use Zoom API to retrieve Data on a periodic basis
* List meetings/calls to ingest
  * Extract items individually
  * Archive Call Audio/Transcription & CDR to relevant s3 bucket
  * Ingest to ES Transcription & CDR
