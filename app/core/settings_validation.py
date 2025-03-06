from typing import Dict, Any, Optional, List, Union
from pydantic import ValidationError

from app.models.instance_settings import InstanceSettings


def validate_settings(settings_data: Dict[str, Any]) -> List[str]:
    """
    Validate settings data against the InstanceSettings model.
    
    Args:
        settings_data: Settings data to validate
        
    Returns:
        List of validation error messages, empty if valid
    """
    try:
        # Create a complete settings object with the provided data
        InstanceSettings(**settings_data)
        return []
    except ValidationError as e:
        # Return validation error messages
        return [f"{error['loc'][0]}: {error['msg']}" for error in e.errors()]


def validate_settings_section(section: str, section_data: Dict[str, Any]) -> List[str]:
    """
    Validate a specific section of settings data.
    
    Args:
        section: The section name (e.g., 'identity', 'behavior')
        section_data: The section data to validate
        
    Returns:
        List of validation error messages, empty if valid
    """
    # Create a dictionary with just the section data
    settings_data = {section: section_data}
    
    try:
        # Create a model instance with just this section
        # We use construct to avoid validating missing sections
        model = InstanceSettings.construct()
        
        # Set and validate just the section
        setattr(model, section, section_data)
        model.__pydantic_self__.fields[section].validate(
            section_data, model.__pydantic_self__.fields[section].outer_type_
        )
        return []
    except ValidationError as e:
        # Return validation error messages
        return [f"{error['loc'][0]}: {error['msg']}" for error in e.errors()]
    except (KeyError, AttributeError):
        # Section doesn't exist in model
        return [f"Invalid settings section: {section}"]


def get_section_schema(section: Optional[str] = None) -> Dict[str, Any]:
    """
    Get JSON schema for the entire settings model or a specific section.
    
    Args:
        section: Optional section name to get schema for
        
    Returns:
        JSON schema as a dictionary
    """
    schema = InstanceSettings.schema()
    
    if section:
        try:
            # Return schema for just the requested section
            return schema["properties"][section]
        except KeyError:
            # Section doesn't exist
            return {}
    
    return schema 