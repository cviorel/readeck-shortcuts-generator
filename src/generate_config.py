#!/usr/bin/env python3

import json
import uuid
import argparse
import sys
from pathlib import Path

def generate_uuid():
    """Generate a UUID v4 string"""
    return str(uuid.uuid4())

def create_label_shortcut(label_config, auth_token, server_url_var_id, article_title_var_id, article_url_var_id):
    """Create a shortcut configuration for a specific label"""
    label = label_config['label']
    name = label_config.get('name', f"🏷️ {label}")
    icon_name = label_config.get('iconName', 'flat_color_tag_2')
    description = label_config.get('description', f"Save article with {label} label")
    success_message = label_config.get('successMessage', f"🏷️ Article saved with {label} label!")
    failure_message = label_config.get('failureMessage', f"❌ Failed to save article with {label} label.")

    return {
        "authToken": auth_token,
        "authentication": "bearer",
        "bodyContent": f'{{\n  "labels": [\n    "{label}"\n  ],\n  "title": "{{{{{article_title_var_id}}}}}",\n  "url": "{{{{{article_url_var_id}}}}}"\n}}',
        "contentType": "application/json",
        "description": description,
        "iconName": icon_name,
        "id": generate_uuid(),
        "method": "POST",
        "name": name,
        "responseHandling": {
            "successMessage": success_message,
            "successOutput": "message",
            "uiType": "toast",
            "failureOutput": "message",
            "failureMessage": failure_message
        },
        "url": f"{{{{{server_url_var_id}}}}}/api/bookmarks",
        "timeout": 10000,
        "followRedirects": True,
        "acceptAllCertificates": False,
        "acceptCookies": True,
        "requireConfirmation": False,
        "launcherShortcut": True,
        "secondaryLauncherShortcut": False,
        "quickSettingsTileShortcut": False,
        "wifiSsid": "",
        "delay": 0,
        "repetitions": {
            "count": 1,
            "interval": 0
        }
    }

def generate_config_from_template(template_path, options):
    """Generate configuration from template file"""

    # Read template
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
    except FileNotFoundError:
        print(f"Error: Template file '{template_path}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading template file: {e}")
        sys.exit(1)

    # Generate UUIDs for all placeholders
    category_id = generate_uuid()
    server_url_var_id = generate_uuid()
    default_label_var_id = generate_uuid()
    article_title_var_id = generate_uuid()
    article_url_var_id = generate_uuid()
    shortcut_id_save_article = generate_uuid()

    # Extract options
    auth_token = options['authToken']
    server_url = options.get('serverUrl', 'http://localhost:8090')
    default_label = options.get('defaultLabel', 'inbox')
    custom_labels = options.get('customLabels', [])

    # Replace placeholders in template
    replacements = {
        '{{CATEGORY_ID}}': category_id,
        '{{AUTH_TOKEN}}': auth_token,
        '{{SERVER_URL_VAR_ID}}': server_url_var_id,
        '{{DEFAULT_LABEL_VAR_ID}}': default_label_var_id,
        '{{ARTICLE_TITLE_VAR_ID}}': article_title_var_id,
        '{{ARTICLE_URL_VAR_ID}}': article_url_var_id,
        '{{SHORTCUT_ID_SAVE_ARTICLE}}': shortcut_id_save_article,
        '{{SERVER_URL}}': server_url,
        '{{DEFAULT_LABEL}}': default_label
    }

    # Apply replacements
    config_content = template_content
    for placeholder, value in replacements.items():
        config_content = config_content.replace(placeholder, value)

    # Parse the JSON to add custom label shortcuts
    try:
        config = json.loads(config_content)
    except json.JSONDecodeError as e:
        print(f"Error parsing generated JSON: {e}")
        sys.exit(1)

    # Add custom label shortcuts
    if custom_labels:
        shortcuts = config['categories'][0]['shortcuts']
        for label_config in custom_labels:
            shortcut = create_label_shortcut(
                label_config,
                auth_token,
                server_url_var_id,
                article_title_var_id,
                article_url_var_id
            )
            shortcuts.append(shortcut)

    return config

def load_config_file(config_path):
    """Load configuration from JSON file"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: Configuration file '{config_path}' not found.")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error parsing configuration file: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading configuration file: {e}")
        sys.exit(1)

def parse_labels_string(labels_string):
    """Parse comma-separated labels string into label configurations"""
    if not labels_string:
        return []

    labels = []
    for label in labels_string.split(','):
        label = label.strip()
        if label:
            labels.append({
                'label': label,
                'name': f"🏷️ {label}",
                'iconName': 'flat_color_tag_2'
            })
    return labels

def main():
    parser = argparse.ArgumentParser(
        description='Generate Readeck shortcuts configuration from template',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Using a configuration file
  python generate_config.py --config my-config.json

  # Using command line options
  python generate_config.py --auth-token "your-token-here" --labels "Work,Tech,Personal"

Configuration file format:
{
  "authToken": "your-auth-token-here",
  "serverUrl": "http://your-server:8090",
  "defaultLabel": "inbox",
  "customLabels": [
    {
      "label": "Work",
      "name": "💼 Work",
      "iconName": "flat_color_briefcase_2",
      "description": "Save article with work-related label"
    },
    {
      "label": "Tech",
      "name": "💻 Tech",
      "iconName": "flat_color_computer_2"
    }
  ]
}
        '''
    )

    parser.add_argument('--config', '-c',
                       help='Path to JSON configuration file')
    parser.add_argument('--template', '-t',
                       default='templates/shortcuts-template.json',
                       help='Path to template file (default: templates/shortcuts-template.json)')
    parser.add_argument('--output', '-o',
                       default='shortcuts-generated.json',
                       help='Output file path (default: shortcuts-generated.json)')
    parser.add_argument('--auth-token',
                       help='Readeck API authentication token')
    parser.add_argument('--server-url',
                       default='http://localhost:8090',
                       help='Readeck server URL (default: http://localhost:8090)')
    parser.add_argument('--default-label',
                       default='inbox',
                       help='Default label for articles (default: inbox)')
    parser.add_argument('--labels',
                       help='Comma-separated list of custom labels')

    args = parser.parse_args()

    # If no arguments provided, show help
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    # Determine configuration source
    if args.config:
        options = load_config_file(args.config)
    else:
        if not args.auth_token:
            print("Error: Auth token is required. Use --auth-token or provide it in config file.")
            sys.exit(1)

        options = {
            'authToken': args.auth_token,
            'serverUrl': args.server_url,
            'defaultLabel': args.default_label,
            'customLabels': parse_labels_string(args.labels)
        }

    # Validate required options
    if 'authToken' not in options or not options['authToken']:
        print("Error: Auth token is required in configuration.")
        sys.exit(1)

    try:
        # Generate configuration
        config = generate_config_from_template(args.template, options)

        # Write output file
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

        print(f"✅ Configuration generated successfully: {args.output}")
        print(f"📊 Generated {len(config['categories'][0]['shortcuts'])} shortcuts")

        if options.get('customLabels'):
            labels = [label['label'] for label in options['customLabels']]
            print(f"🏷️  Custom labels: {', '.join(labels)}")

    except Exception as e:
        print(f"Error generating configuration: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
