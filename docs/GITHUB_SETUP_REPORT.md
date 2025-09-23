# GitHub Repository Setup Guide - MCP Server Template

**Date:** September 23, 2025
**Template Version:** 1.0
**Applicable To:** MCP Server Repositories
**Last Updated:** 2025-09-23

---

## 📋 Executive Summary

This document provides a comprehensive template for setting up modern GitHub features in MCP server repositories. The HandBrake MCP Server repository serves as the reference implementation, featuring enterprise-grade CI/CD, documentation, community management, and release automation.

**Key Features Implemented:**
- ✅ Complete CI/CD pipeline with multi-platform testing
- ✅ Automated documentation deployment (GitHub Pages + MkDocs)
- ✅ Professional release management with changelog generation
- ✅ Community health automation (stale issues, metrics)
- ✅ Security policy and contribution guidelines
- ✅ Wiki automation and integration
- ✅ Issue/PR templates and automation
- ✅ Release validation and orchestration

---

## 🏗️ Repository Structure Overview

```
.github/
├── workflows/                    # GitHub Actions CI/CD
│   ├── ci.yml                   # Main CI/CD pipeline
│   ├── docs.yml                 # Documentation deployment
│   ├── release-orchestration.yml # Release automation
│   ├── release-validation.yml   # Release quality checks
│   ├── community-health.yml     # Community management
│   ├── dependency-updates.yml   # Automated dependency updates
│   ├── docker.yml              # Docker build automation
│   └── version-management.yml  # Version bump automation
├── ISSUE_TEMPLATE/              # Issue creation templates
│   ├── bug-report.md
│   └── feature-request.md
├── CODE_OF_CONDUCT.md           # Community behavior guidelines
├── CONTRIBUTING.md              # Development contribution guide
├── PULL_REQUEST_TEMPLATE.md     # PR creation template
├── SECURITY.md                  # Security vulnerability reporting
├── link-check-config.json       # Documentation link validation
└── profile/
    └── README.md               # Repository profile showcase
```

---

## ⚙️ GitHub Actions Workflows

### 1. **CI/CD Pipeline (`ci.yml`)**

#### **Purpose**
Complete continuous integration and deployment pipeline with quality gates, testing, and automated releases.

#### **Key Features**
```yaml
# Multi-stage pipeline
jobs:
  quality-checks:     # Code quality validation
  integration-tests:  # Real CLI integration testing
  test-suite:        # Cross-platform unit testing
  build-dxt:         # Package building
  release:           # Automated releases
  deploy-docs:       # Documentation deployment
```

#### **Quality Gates**
- **Black**: Code formatting
- **isort**: Import sorting
- **flake8**: Linting
- **mypy**: Type checking
- **bandit**: Security scanning
- **Real CLI Testing**: Integration tests with actual dependencies

#### **Implementation Steps**
1. Copy `ci.yml` to your repository
2. Update Python version and dependencies
3. Modify CLI installation commands for your specific tool
4. Update package building commands
5. Configure release triggers and permissions

### 2. **Documentation Deployment (`docs.yml`)**

#### **Purpose**
Automated documentation building and deployment to GitHub Pages using MkDocs.

#### **Features**
- **MkDocs Material**: Professional documentation theme
- **Versioned Docs**: Support for multiple versions
- **Search Integration**: Built-in search functionality
- **Wiki Sync**: Automatic wiki updates

#### **Required Files**
```yaml
# mkdocs.yml
site_name: "Your MCP Server"
theme:
  name: material
plugins:
  - search
  - git-revision-date-localized
nav:
  - Home: index.md
  - API: api.md
  # ... navigation structure
```

#### **Setup Steps**
1. Create `mkdocs.yml` configuration
2. Set up documentation structure in `docs/` folder
3. Enable GitHub Pages in repository settings
4. Configure custom domain (optional)

### 3. **Release Orchestration (`release-orchestration.yml`)**

#### **Purpose**
Comprehensive release management with validation, documentation, and community notifications.

#### **Workflow Stages**
```yaml
jobs:
  analyze-release:     # Determine release type and requirements
  version-sync:        # Update version numbers across all files
  generate-artifacts:  # Build and validate release packages
  update-documentation: # Deploy updated docs
  community-announcement: # Notify community of release
  validate-release:    # Final quality checks
  maintenance:         # Post-release cleanup
```

#### **Features**
- **Changelog Generation**: Automatic git history analysis
- **Version Synchronization**: Update versions in all relevant files
- **Community Notifications**: GitHub Discussions and automated posts
- **Release Validation**: Package integrity and functionality checks

### 4. **Community Health (`community-health.yml`)**

#### **Purpose**
Automated community management and repository maintenance.

#### **Features**
- **Stale Issue Management**: Auto-close inactive issues/PRs
- **Community Metrics**: Generate repository health reports
- **Link Validation**: Check documentation links for broken URLs

#### **Configuration**
```yaml
stale-issue-message: |
  This issue has been marked as stale...
stale-pr-message: |
  This PR has been marked as stale...
```

### 5. **Version Management (`version-management.yml`)**

#### **Purpose**
Automated version bumping and release preparation.

#### **Workflow Triggers**
```yaml
on:
  workflow_dispatch:
    inputs:
      version_type:  # patch, minor, major
      create_release: # boolean
```

#### **Features**
- **Semantic Versioning**: Automated version calculation
- **Multi-file Updates**: Update version in manifest, pyproject.toml, __init__.py
- **Git Operations**: Automatic commits and tagging

---

## 📝 Issue and PR Templates

### **Bug Report Template (`ISSUE_TEMPLATE/bug-report.md`)**

#### **Structure**
```markdown
---
name: Bug Report
description: Report a bug or unexpected behavior
title: "[BUG] "
labels: ["bug", "triage"]
---

## Bug Description
<!-- Clear description of the issue -->

## Steps to Reproduce
<!-- Detailed reproduction steps -->

## Environment
- OS, Python version, dependencies
- Installation method
- Error logs and stack traces
```

### **Feature Request Template (`ISSUE_TEMPLATE/feature-request.md`)**

#### **Structure**
```markdown
---
name: Feature Request
description: Suggest a new feature or enhancement
title: "[FEATURE] "
labels: ["enhancement", "triage"]
---

## Feature Summary
## Problem Statement
## Proposed Solution
## Alternative Solutions
## Use Cases
## Implementation Notes
```

### **PR Template (`PULL_REQUEST_TEMPLATE.md`)**

#### **Checklist Items**
- [ ] Code follows project style guidelines
- [ ] Tests added for new functionality
- [ ] Documentation updated
- [ ] Self-review completed
- [ ] Related issues linked

---

## 📚 Documentation System

### **MkDocs Configuration**

#### **Essential Configuration**
```yaml
site_name: "Your MCP Server"
site_description: "Professional MCP server for [purpose]"

theme:
  name: material
  features:
    - content.code.annotate
    - navigation.expand
    - search.highlight

plugins:
  - search
  - git-revision-date-localized
  - git-committers

nav:
  - Home: index.md
  - Installation: installation.md
  - API Reference: api/
  - Development: development/
```

### **Documentation Structure**
```
docs/
├── index.md              # Homepage
├── installation.md       # Setup instructions
├── configuration.md      # Configuration guide
├── usage/               # Usage guides
│   ├── basic.md
│   └── advanced.md
├── api/                 # API documentation
│   ├── tools.md
│   └── config.md
├── development/         # Development docs
│   ├── contributing.md
│   ├── testing.md
│   └── building.md
├── hooks.py             # MkDocs hooks for dynamic content
└── assets/              # Static assets
```

### **GitHub Pages Setup**

1. **Enable Pages**: Repository Settings → Pages → Source: GitHub Actions
2. **Custom Domain** (Optional):
   ```yaml
   # mkdocs.yml
   extra:
     # Custom domain configuration
   ```
3. **CNAME File**: Create `docs/CNAME` for custom domains

---

## 🔒 Security and Compliance

### **Security Policy (`SECURITY.md`)**

#### **Required Sections**
- Supported versions table
- Vulnerability reporting process
- Response timeline commitments
- Security considerations
- Contact information

### **Code of Conduct (`CODE_OF_CONDUCT.md`)**

#### **Community Standards**
- Expected behavior guidelines
- Unacceptable behavior examples
- Enforcement responsibilities
- Reporting procedures

### **Contributing Guide (`CONTRIBUTING.md`)**

#### **Development Workflow**
- Prerequisites and setup
- Branch naming conventions
- Commit message standards
- Testing requirements
- Code review process

---

## 🤖 Automation Features

### **Release Automation**

#### **Changelog Generation**
```bash
# Automatic changelog from git history
PREVIOUS_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "")
if [ -z "$PREVIOUS_TAG" ]; then
  git log --pretty=format:"* %s (%h)" --reverse > changelog.md
else
  git log --pretty=format:"* %s (%h)" "$PREVIOUS_TAG..HEAD" > changelog.md
fi
```

#### **Version Synchronization**
- Update version in `pyproject.toml`
- Update version in package `__init__.py`
- Update version in DXT manifest
- Update documentation version placeholders

### **Community Management**

#### **Stale Issue Automation**
```yaml
stale-issue-message: |
  This issue has been marked as stale...
days-before-stale: 60
days-before-close: 14
```

#### **Link Validation**
```json
{
  "ignorePatterns": [
    "^http://localhost"
  ],
  "replacementPatterns": [
    {
      "pattern": "^/",
      "replacement": "https://your-repo.github.io/your-project/"
    }
  ]
}
```

---

## 🚀 Release Process

### **Automated Release Flow**

1. **Code Quality**: Run all tests and quality checks
2. **Version Bump**: Automatic semantic versioning
3. **Package Building**: Create DXT packages with checksums
4. **Documentation**: Update and deploy docs
5. **Release Creation**: Generate changelog and create GitHub release
6. **Community Notification**: Post to discussions and update wiki
7. **Validation**: Verify release integrity
8. **Maintenance**: Close milestones and update labels

### **Release Checklist**

#### **Pre-Release**
- [ ] All tests passing
- [ ] Documentation updated
- [ ] Changelog generated
- [ ] Version numbers synchronized

#### **Release**
- [ ] GitHub release created
- [ ] Tags pushed
- [ ] Artifacts uploaded
- [ ] Community notified

#### **Post-Release**
- [ ] Release validated
- [ ] Documentation deployed
- [ ] Wiki updated
- [ ] Milestones closed

---

## 🔧 Repository Configuration

### **GitHub Settings**

#### **Branches**
- **Default Branch**: `main`
- **Branch Protection**: Require PR reviews, status checks
- **Required Status Checks**: CI, integration tests

#### **Features**
- **Issues**: Enabled
- **Discussions**: Enabled
- **Wiki**: Enabled
- **Pages**: Enabled (GitHub Actions source)

#### **Security**
- **Dependabot**: Enable for dependency updates
- **CodeQL**: Enable for security scanning
- **Secret Scanning**: Enable

### **Repository Topics**
```
mcp, mcp-server, automation, [domain-specific-tags]
```

### **Repository Description**
```
Professional MCP server for [purpose] with comprehensive automation and documentation
```

---

## 📊 Monitoring and Metrics

### **CI/CD Metrics**
- **Test Coverage**: Track with codecov or similar
- **Build Success Rate**: Monitor pipeline reliability
- **Release Frequency**: Track release cadence

### **Community Metrics**
- **Issue Response Time**: Monitor and report
- **PR Review Time**: Track review efficiency
- **Community Growth**: Stars, forks, contributors

### **Quality Metrics**
- **Code Quality**: Maintain high standards
- **Documentation**: Keep up-to-date
- **Security**: Regular dependency updates

---

## 🛠️ Customization Guide

### **Adapting for Your MCP Server**

#### **1. Update Repository Information**
```yaml
# ci.yml
env:
  PYTHON_VERSION: '3.8'  # Adjust as needed

# mkdocs.yml
site_name: "Your MCP Server Name"
site_description: "Description of your server"

# DXT manifest
{
  "name": "your-mcp-server",
  "display_name": "Your MCP Server"
}
```

#### **2. Modify CLI Dependencies**
```yaml
# ci.yml - Update installation commands
- name: Install Your CLI Tool
  run: |
    # Replace with your tool's installation commands
    sudo apt install -y your-tool
```

#### **3. Update Testing Commands**
```yaml
# ci.yml - Modify test commands
- name: Run Integration Tests
  run: |
    # Replace with your integration test commands
    python scripts/run_tests.py integration
```

#### **4. Customize Documentation**
- Update `docs/` content for your specific server
- Modify navigation in `mkdocs.yml`
- Update API documentation structure

#### **5. Adjust Release Process**
- Modify package building in `ci.yml`
- Update release notes template
- Customize community notification content

---

## 📋 Implementation Checklist

### **Phase 1: Core Setup**
- [ ] Copy `.github/` directory structure
- [ ] Update repository information in all files
- [ ] Configure GitHub repository settings
- [ ] Set up GitHub Pages
- [ ] Enable required repository features

### **Phase 2: CI/CD Configuration**
- [ ] Update Python version and dependencies
- [ ] Modify CLI tool installation commands
- [ ] Configure package building process
- [ ] Update test commands and coverage settings

### **Phase 3: Documentation Setup**
- [ ] Create MkDocs configuration
- [ ] Set up documentation structure
- [ ] Configure GitHub Pages deployment
- [ ] Update all documentation content

### **Phase 4: Release Automation**
- [ ] Configure version management workflow
- [ ] Set up release orchestration
- [ ] Test release validation process
- [ ] Configure community notification templates

### **Phase 5: Community Features**
- [ ] Enable GitHub Discussions
- [ ] Set up wiki automation
- [ ] Configure community health monitoring
- [ ] Test all issue/PR templates

### **Phase 6: Testing and Validation**
- [ ] Run full CI/CD pipeline
- [ ] Test release process
- [ ] Validate documentation deployment
- [ ] Check all automation features

---

## 🎯 Best Practices

### **Repository Management**
1. **Keep Templates Updated**: Regularly update issue/PR templates
2. **Monitor CI/CD Performance**: Optimize build times and reliability
3. **Maintain Documentation**: Keep docs current with code changes
4. **Community Engagement**: Actively manage discussions and issues

### **Security Considerations**
1. **Regular Updates**: Keep dependencies updated
2. **Security Scanning**: Monitor for vulnerabilities
3. **Access Control**: Use appropriate permission levels
4. **Audit Logs**: Review repository activity regularly

### **Performance Optimization**
1. **Cache Dependencies**: Use GitHub Actions caching
2. **Parallel Jobs**: Run independent jobs in parallel
3. **Selective Triggers**: Only run necessary checks
4. **Artifact Management**: Clean up old artifacts

---

## 📞 Support and Resources

### **Documentation Links**
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [MkDocs Documentation](https://www.mkdocs.org/)
- [Material Theme](https://squidfunk.github.io/mkdocs-material/)
- [GitHub Pages Guide](https://docs.github.com/en/pages)

### **Community Resources**
- [GitHub Community Forum](https://github.community/)
- [GitHub Actions Community](https://github.com/actions)
- [MCP Community](https://modelcontextprotocol.io/community)

### **Template Updates**
This guide will be updated as new features are added to the reference implementation. Check the [HandBrake MCP Server repository](https://github.com/sandraschi/handbrakemcp) for the latest template version.

---

## 📈 Success Metrics

### **Repository Health Indicators**
- **CI/CD Reliability**: >95% success rate
- **Issue Response Time**: <48 hours average
- **Documentation Coverage**: >90%
- **Community Engagement**: Active discussions and contributions

### **Quality Metrics**
- **Test Coverage**: >80%
- **Code Quality**: Passing all linting checks
- **Security Score**: Regular dependency updates
- **Release Frequency**: Consistent release cadence

---

**This comprehensive GitHub setup template transforms MCP server repositories into professional, enterprise-grade open source projects with full automation, documentation, and community management capabilities.** 🚀

