"""MkDocs hooks for dynamic content generation."""

import json
import os
from pathlib import Path


def on_pre_build(config, **kwargs):
    """Pre-build hook to generate dynamic content."""

    # Get version from manifest
    try:
        manifest_path = Path(__file__).parent.parent / "dxt" / "manifest.json"
        with open(manifest_path, 'r') as f:
            manifest = json.load(f)
        version = manifest.get('version', '0.1.0')
    except:
        version = '0.1.0'

    # Update version in config
    config.extra['version'] = version

    return config


def on_page_markdown(markdown, page, config, **kwargs):
    """Process page markdown for dynamic content."""

    # Replace version placeholders
    version = config.extra.get('version', '0.1.0')
    markdown = markdown.replace('{{ version }}', version)
    markdown = markdown.replace('{{VERSION}}', version)

    return markdown

