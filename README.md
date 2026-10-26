# Multimodal Document Intelligence

## Problem
Documents such as invoices, receipts, CVs, and contracts often contain important information in both text and visual layout. The goal of this project is to extract that information reliably into structured data.

## Input
PDF files or images containing supported business documents.

## Supported Documents
- Invoice
- Receipt
- CV
- Contract

## Output
Structured and validated JSON containing the relevant fields extracted from the uploaded document.

## Core Reliability Rule
The system must not invent missing information. If a field cannot be reliably identified, it should be returned as missing, null, or reported with an appropriate warning.