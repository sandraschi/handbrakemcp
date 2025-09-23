# Security Policy

## Supported Versions

We take security seriously and actively maintain security updates for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |
| < 0.1.0 | :x:                |

## Reporting a Vulnerability

If you discover a security vulnerability in HandBrake MCP Server, please help us by reporting it responsibly.

### How to Report

**Please DO NOT report security vulnerabilities through public GitHub issues.**

Instead, please report security vulnerabilities by emailing:
- **Email**: security@sandraschi.dev (create this email alias if needed)
- **Subject**: `[SECURITY] HandBrake MCP Vulnerability Report`

### What to Include

Please include the following information in your report:

1. **Description**: A clear description of the vulnerability
2. **Impact**: What an attacker could achieve by exploiting this vulnerability
3. **Steps to Reproduce**: Detailed steps to reproduce the issue
4. **Proof of Concept**: Code or commands demonstrating the vulnerability
5. **Environment**: Your system details (OS, Python version, etc.)
6. **Suggested Fix**: If you have suggestions for fixing the issue

### Response Timeline

We will acknowledge your report within **48 hours** and provide a more detailed response within **7 days** indicating our next steps.

We will keep you informed about our progress throughout the process of fixing the vulnerability.

## Security Considerations

### Data Handling

- **No user data storage**: The server processes video files but does not store user data
- **File validation**: All input files are validated for size, type, and path safety
- **Temporary files**: Transcoding uses temporary files that are cleaned up automatically

### Network Security

- **Local execution**: By default, the server runs locally and doesn't expose ports
- **MCP protocol**: Uses the Model Context Protocol for secure AI integration
- **No external APIs**: Does not make calls to external services by default

### Dependencies

- **Regular updates**: Dependencies are regularly updated for security patches
- **Minimal dependencies**: Only essential packages are included
- **Vulnerability scanning**: Automated security scanning is performed on all code

## Security Best Practices

### For Users

1. **Install from trusted sources**: Only download releases from the official GitHub repository
2. **Verify signatures**: Check release checksums when available
3. **Keep updated**: Regularly update to the latest version
4. **Secure environment**: Run in a secure environment with appropriate file permissions
5. **Input validation**: Be cautious with input file sources

### For Contributors

1. **Code review**: All changes undergo security review
2. **Dependency checks**: New dependencies are vetted for security
3. **Testing**: Security implications are considered in testing
4. **Documentation**: Security considerations are documented

## Known Security Considerations

### File Processing
- **Path traversal**: Prevented through input validation
- **Large files**: Size limits prevent resource exhaustion
- **Malicious files**: HandBrake CLI handles most file-based attacks

### Process Execution
- **Command injection**: Prevented through proper argument handling
- **Resource limits**: Concurrent job limits prevent DoS
- **Process isolation**: HandBrake CLI runs in separate process

## Security Updates

Security updates will be released as patch versions with the following naming convention:
- `x.y.z-security` for security-only releases
- Regular patch releases may include security fixes

## Contact

For security-related questions or concerns:
- **Security Issues**: Use the reporting process above
- **General Questions**: Create a [GitHub Discussion](https://github.com/sandraschi/handbrake-mcp/discussions)
- **Documentation**: Check the [security section](https://sandraschi.github.io/handbrake-mcp/security/)

Thank you for helping keep HandBrake MCP Server secure! 🔒

