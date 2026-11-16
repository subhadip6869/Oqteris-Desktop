# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |

## Reporting a Vulnerability

OriginSD and the Oqteris development team take security seriously. If you discover a security vulnerability in Oqteris, please follow these steps:

1. **Do not** disclose vulnerabilities publicly in issues, discussions, or social media.
2. Report the vulnerability privately via GitHub Security Advisories at [https://github.com/subhadip6869/Oqteris-Desktop/security/advisories/new](https://github.com/subhadip6869/Oqteris-Desktop/security/advisories/new) or by emailing the project maintainer at `subhadip6869@users.noreply.github.com`.
3. Provide detailed steps to reproduce the vulnerability, including sample PDFs (sanitized of sensitive data), environment information, and attack vectors.

## PDF Security Architecture

Oqteris adheres to strict security principles for handling PDF content:
- **Untrusted Input Handling**: All PDF files are treated as untrusted data. Memory limits and safe parsing guards prevent resource exhaustion.
- **Embedded Scripts & Executables**: Embedded JavaScript and launch actions in PDF files are disabled to prevent arbitrary execution vulnerabilities.
- **External Links**: User confirmation is required before opening external web links or external file references.
- **Digital Signatures & Trust**: Cryptographic signature validation is strictly decoupled from certificate trust evaluation. Self-signed or unverified certificates are flagged, and incremental save workflows preserve original digital signatures without silent corruption.
- **Credential Storage**: Passwords, private keys, and certificate credentials are never written to disk in plaintext or logged in debug traces.
