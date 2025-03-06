# Instance Settings API

This document describes the API endpoints for managing AI Agent instance settings.

## Overview

The Instance Settings API allows you to:
- Retrieve the complete settings for an instance
- Update the entire settings object
- Update specific sections of settings
- Reset settings to default values
- Get the JSON schema for validation

Each instance has a structured settings object with the following main sections:
- `identity`: Branding and identity settings
- `knowledge`: Knowledge acquisition and management settings
- `behavior`: Agent behavior and communication settings
- `interaction`: Website interaction capabilities
- `appearance`: Chat widget appearance settings
- `integration`: External integration settings
- `compliance`: Data handling and compliance settings

## Endpoints

### Get Instance Settings

Retrieves the complete settings for an instance.

**URL**: `GET /api/v1/instances/{instance_id}`

**URL Parameters**:
- `instance_id`: UUID of the instance

**Response**:
```json
{
  "id": "uuid",
  "api_key": "string",
  "name": "string",
  "website_url": "string",
  "settings": {
    "version": "1.0",
    "identity": { ... },
    "knowledge": { ... },
    "behavior": { ... },
    "interaction": { ... },
    "appearance": { ... },
    "integration": { ... },
    "compliance": { ... }
  },
  "is_active": true,
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### Update Instance Settings

Updates the entire settings object with a deep merge (preserves nested values not included in the update).

**URL**: `PATCH /api/v1/instances/{instance_id}/settings`

**URL Parameters**:
- `instance_id`: UUID of the instance

**Request Body**:
```json
{
  "identity": {
    "name": "Updated Bot Name",
    "primary_color": "#FF5500"
  },
  "behavior": {
    "tone": "professional"
  }
}
```

**Response**: Updated instance object (same as GET response)

### Update Settings Section

Updates a specific section of the settings with a deep merge.

**URL**: `PATCH /api/v1/instances/{instance_id}/settings/{section}`

**URL Parameters**:
- `instance_id`: UUID of the instance
- `section`: Section name (e.g., "identity", "behavior")

**Request Body**:
```json
{
  "tone": "professional",
  "response_length": "concise"
}
```

**Response**: Updated instance object (same as GET response)

### Get Settings Schema

Retrieves the JSON schema for the settings model or a specific section.

**URL**: `GET /api/v1/instances/{instance_id}/settings/schema`

**URL Parameters**:
- `instance_id`: UUID of the instance

**Query Parameters**:
- `section` (optional): Section name to get schema for

**Response**:
```json
{
  "title": "InstanceSettings",
  "type": "object",
  "properties": {
    "version": { ... },
    "identity": { ... },
    ...
  },
  "required": [ ... ]
}
```

### Reset Settings

Resets instance settings to default values.

**URL**: `POST /api/v1/instances/{instance_id}/settings/reset`

**URL Parameters**:
- `instance_id`: UUID of the instance

**Response**: Updated instance object (same as GET response)

## Settings Schema Reference

### Identity Settings

```json
{
  "name": "AI Assistant",
  "description": "Your AI assistant to help with website navigation and tasks.",
  "logo_url": null,
  "primary_color": "#3B82F6",
  "secondary_color": null,
  "accent_color": null
}
```

### Knowledge Settings

```json
{
  "crawling": {
    "enabled": true,
    "depth": 2,
    "include_patterns": [],
    "exclude_patterns": ["*/admin*", "*/login*"],
    "frequency": "weekly",
    "require_authentication": false
  },
  "manual_sources": {
    "enable_document_upload": true,
    "enable_faq_builder": true,
    "enable_knowledge_snippets": true
  },
  "learning": {
    "enable_learning_from_interactions": true,
    "require_admin_review": true,
    "feedback_collection": true
  }
}
```

### Behavior Settings

```json
{
  "tone": "friendly",
  "response_length": "balanced",
  "language": "en",
  "greeting": "Hello! I'm your AI assistant. How can I help you today?",
  "fallback_message": "I'm not sure I understand. Could you please rephrase your question or request?",
  "proactivity_level": "medium"
}
```

### Interaction Settings

```json
{
  "global_permission_level": "guided",
  "element_permissions": {
    "buttons": true,
    "forms": true,
    "links": true,
    "inputs": true,
    "file_uploads": false
  },
  "protected_selectors": [],
  "require_confirmation": true,
  "highlight_color": "#3B82F6",
  "highlight_animation": true,
  "interaction_speed": "medium"
}
```

### Appearance Settings

```json
{
  "position": "bottom-right",
  "size": "medium",
  "theme": "light",
  "show_branding": true,
  "custom_css": null,
  "bubble_icon_url": null,
  "mobile_position": "bottom"
}
```

### Integration Settings

```json
{
  "crm_webhook_url": null,
  "analytics_enabled": true,
  "enable_ticketing": false,
  "email_notifications": false,
  "deployment": {
    "initialization": "delayed",
    "excluded_paths": [],
    "included_paths": [],
    "show_on_mobile": true
  }
}
```

### Compliance Settings

```json
{
  "data_retention_days": 90,
  "detect_pii": true,
  "mask_pii": true,
  "gdpr_compliance": true,
  "ccpa_compliance": true,
  "require_consent": true
}
``` 