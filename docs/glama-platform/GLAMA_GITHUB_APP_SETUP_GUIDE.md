# 🚀 Glama.ai GitHub App Setup Guide for HandBrake MCP Server

## Executive Summary

This guide provides step-by-step instructions for installing and configuring the Glama.ai GitHub App on the `handbrakemcp` repository to enable automatic quality monitoring and platform integration.

---

## 📋 Prerequisites

### Repository Requirements
- [x] Repository: `sandraschi/handbrakemcp`
- [x] Admin access to repository settings
- [x] Glama.ai account (optional but recommended)

### Configuration Files Ready
- [x] `glama.yml` - Platform metadata ✅
- [x] `.github/glama-webhook.yml` - Webhook configuration ✅
- [x] `.github/apps/glama-github-app.yml` - App configuration ✅

---

## 🔧 Installation Steps

### Step 1: Access GitHub App Marketplace

1. **Navigate to Glama.ai GitHub App**
   ```
   URL: https://github.com/apps/glama-ai
   ```

2. **Click "Install"**
   - Located in the top-right corner of the app page
   - This will redirect you to GitHub's installation flow

### Step 2: Select Installation Scope

1. **Choose Account Type**
   - Select your personal account (`sandraschi`) or organization
   - For this repository, use your personal account

2. **Select Repository**
   - Choose **"Only select repositories"**
   - Search for: `handbrakemcp`
   - Select: `sandraschi/handbrakemcp`

3. **Grant Permissions**
   The app will request the following permissions:

   #### Repository Permissions (Required)
   - ✅ **Contents**: Read access to repository contents
   - ✅ **Metadata**: Read access to repository information
   - ✅ **Pull requests**: Read access to pull request data
   - ✅ **Issues**: Read access to issue data
   - ✅ **Releases**: Read access to release information
   - ✅ **Workflows**: Read access to workflow runs

   #### Account Permissions (Required)
   - ✅ **Email addresses**: Read access to email addresses
   - ✅ **Followers**: Read access to followers

### Step 3: Complete Installation

1. **Review Permissions**
   - Verify all required permissions are granted
   - Ensure no additional permissions are requested

2. **Click "Install"**
   - This completes the GitHub App installation
   - You will be redirected back to GitHub

---

## ⚙️ Post-Installation Configuration

### Verify Installation

1. **Check Repository Settings**
   ```
   GitHub → Repository → Settings → Integrations & services
   ```
   - Look for "Glama.ai" in the installed apps list
   - Verify status shows "Installed"

2. **Check Webhook Configuration**
   ```
   GitHub → Repository → Settings → Webhooks
   ```
   - Look for webhook with URL containing `glama.ai`
   - Verify status shows green checkmark
   - Check recent deliveries for successful responses

### Configure Repository Metadata

**Important:** Update your repository settings for optimal Glama.ai indexing:

#### Repository Description
```
Location: GitHub → Repository → Settings → General → Description
Recommended: "FastMCP 2.12 compatible MCP server for HandBrake video transcoding - Gold Status Certified 🏆"
```

#### Repository Topics
```
Location: GitHub → Repository → Settings → Topics
Recommended Topics:
handbrakemcp, mcp-server, handbrake, video-transcoding, fastmcp, gold-status, production-ready, enterprise-grade, media-processing, automation, python, cli-tools, transcoding, video-tools, mcp-tools
```

---

## 🔍 Testing Integration

### Verify Real-time Sync

1. **Make a Test Commit**
   ```bash
   # Make a small change to trigger webhook
   echo "# Test commit for Glama.ai integration" >> test_glama.md
   git add test_glama.md
   git commit -m "test: Verify Glama.ai webhook integration"
   git push origin main
   ```

2. **Check Webhook Delivery**
   ```
   GitHub → Repository → Settings → Webhooks
   ```
   - Click on the Glama.ai webhook
   - Check "Recent Deliveries"
   - Verify HTTP 200 responses

3. **Monitor Glama.ai Platform**
   - Visit: https://glama.ai
   - Search for: `handbrakemcp`
   - Verify repository appears with updated information

### Validate Quality Monitoring

1. **Check CI/CD Integration**
   - Push a commit to trigger the CI pipeline
   - Verify the `glama-optimization` job runs successfully
   - Check that quality reports are generated

2. **Verify Quality Score**
   - The CI pipeline will validate:
     - Zero print statements
     - 100% test pass rate
     - Documentation completeness
     - MCPB configuration validity

---

## 📊 Expected Results

### Immediate Results (Post-Installation)
- ✅ GitHub App installed and active
- ✅ Webhooks configured and working
- ✅ Repository indexed by Glama.ai

### Short-term Results (24-48 hours)
- 📈 Repository appears in Glama.ai search results
- 📊 Quality score calculated and displayed
- 🏆 Gold Status badge visible (if maintained)

### Long-term Results (1-2 weeks)
- 🔄 Real-time updates on code changes
- 📈 Improved search rankings
- 🤝 Enhanced community visibility
- 📊 Detailed analytics and metrics

---

## 🛠️ Troubleshooting

### Common Issues

#### App Not Appearing in Marketplace
**Solution:**
- Ensure you're logged into GitHub
- Try accessing the URL directly: `https://github.com/apps/glama-ai`
- Clear browser cache and try again

#### Repository Not Found During Installation
**Solution:**
- Verify repository name: `sandraschi/handbrakemcp`
- Ensure you have admin access to the repository
- Try refreshing the installation page

#### Webhook Delivery Failing
**Solution:**
- Check webhook URL configuration
- Verify repository permissions
- Contact Glama.ai support: `support@glama.ai`

#### Quality Score Not Updating
**Solution:**
- Ensure all CI/CD workflows are passing
- Verify documentation files are present
- Check that `glama.yml` is properly configured

### Support Resources

#### Glama.ai Support
- **Email**: support@glama.ai
- **Platform**: https://glama.ai
- **Documentation**: https://docs.glama.ai

#### GitHub App Documentation
- **GitHub Apps**: https://docs.github.com/en/apps
- **Webhooks**: https://docs.github.com/en/webhooks

---

## 🎯 Success Checklist

### Installation Complete ✅
- [ ] GitHub App installed on repository
- [ ] Required permissions granted
- [ ] Repository selected for integration

### Configuration Complete ✅
- [ ] Repository description updated
- [ ] Repository topics added
- [ ] Webhook configuration verified

### Integration Verified ✅
- [ ] Webhook deliveries successful
- [ ] Repository appears on Glama.ai
- [ ] Quality score calculated
- [ ] CI/CD integration working

### Optimization Applied ✅
- [ ] Gold Status maintained
- [ ] Real-time updates active
- [ ] Enhanced visibility achieved

---

## 🚀 Requesting Platform Rescan

After successful installation and configuration, request a Glama.ai platform rescan:

### When to Request
- ✅ After initial installation
- ✅ After major feature releases
- ✅ After quality improvements
- ✅ After documentation updates

### How to Request
1. **Use the email template**: `docs/glama-platform/GLAMA_RESCAN_EMAIL.txt`
2. **Follow the guide**: `docs/glama-platform/GLAMA_AI_RESCAN_GUIDE.md`
3. **Send to**: `support@glama.ai`

### Expected Timeline
- **Request Submission**: Immediate
- **Processing Time**: 24-72 hours
- **Notification**: Email confirmation
- **Results**: Updated platform listing

---

## 📈 Monitoring and Maintenance

### Regular Monitoring
- **Weekly**: Check webhook delivery status
- **Monthly**: Verify quality score maintenance
- **Quarterly**: Review platform analytics

### Maintenance Tasks
- [ ] Monitor repository visibility
- [ ] Track quality metric changes
- [ ] Respond to platform feedback
- [ ] Update configuration as needed

### Quality Maintenance
- [ ] Keep all tests passing (100%)
- [ ] Maintain zero print statements
- [ ] Update documentation regularly
- [ ] Monitor CI/CD pipeline health

---

## 🎉 Achievement Summary

**Successful Glama.ai GitHub App Integration:**
- ✅ Enterprise-grade platform integration
- ✅ Real-time quality monitoring
- ✅ Enhanced repository visibility
- ✅ Professional credibility signals
- ✅ Automated Gold Status maintenance

**Result:** Your HandBrake MCP server is now fully integrated with Glama.ai's professional MCP ecosystem! 🏆

---

**Installation Guide Version:** 1.0
**Last Updated:** October 11, 2025
**Repository:** handbrakemcp
**Platform Integration:** Glama.ai GitHub App
**Target Achievement:** Gold Status Certification
