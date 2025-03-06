import pytest
from uuid import uuid4
import copy
from fastapi import HTTPException

from app.models.instance_settings import get_default_settings, InstanceSettings
from app.services.instance_service import InstanceService
from app.core.settings_validation import validate_settings, validate_settings_section


class MockDB:
    """Mock database session for testing"""
    def __init__(self):
        self.instances = {}
        
    async def execute(self, query):
        # This is a simplified mock that handles our test cases
        if hasattr(query, 'whereclause'):
            # Extract instance_id from the where clause (simplified)
            instance_id = query.whereclause.right.value
            if query.is_update:
                # Handle update
                for key, value in query._values.items():
                    setattr(self.instances[instance_id], key, value)
            return MockResult(self.instances.get(instance_id))
        return MockResult(list(self.instances.values()))
    
    async def commit(self):
        pass
        
    async def refresh(self, instance):
        pass
        
    def add(self, instance):
        self.instances[instance.id] = instance


class MockResult:
    """Mock query result"""
    def __init__(self, data):
        self.data = data
        
    def scalar_one_or_none(self):
        return self.data
        
    def scalars(self):
        return self
        
    def all(self):
        return self.data if isinstance(self.data, list) else [self.data]


class MockInstance:
    """Mock instance for testing"""
    def __init__(self, id, settings):
        self.id = id
        self.settings = settings
        self.name = "Test Instance"
        self.website_url = "https://example.com"
        self.is_active = True
        
    @staticmethod
    def from_orm(db_instance):
        # Simple conversion for testing
        return {
            "id": db_instance.id,
            "name": db_instance.name,
            "website_url": db_instance.website_url,
            "settings": db_instance.settings,
            "is_active": db_instance.is_active
        }


@pytest.fixture
def instance_service():
    """Fixture to create a test instance service"""
    db = MockDB()
    return InstanceService(db)


@pytest.fixture
def test_instance_id():
    """Fixture to provide a test instance ID"""
    return uuid4()


@pytest.fixture
def default_settings():
    """Fixture to provide default settings"""
    return get_default_settings()


async def test_update_instance_settings(instance_service, test_instance_id, default_settings):
    """Test updating instance settings"""
    # Setup a test instance
    instance_service.db.instances[test_instance_id] = MockInstance(
        test_instance_id, 
        default_settings
    )
    
    # Update just the identity section
    new_settings = {
        "identity": {
            "name": "Updated Name",
            "description": "Updated description",
            "primary_color": "#FF0000"
        }
    }
    
    result = await instance_service.update_instance_settings(
        test_instance_id,
        new_settings
    )
    
    # Check that settings were updated correctly
    assert result["settings"]["identity"]["name"] == "Updated Name"
    assert result["settings"]["identity"]["description"] == "Updated description"
    assert result["settings"]["identity"]["primary_color"] == "#FF0000"
    
    # Check that other sections remain unchanged
    assert result["settings"]["behavior"]["tone"] == default_settings["behavior"]["tone"]


async def test_update_settings_section(instance_service, test_instance_id, default_settings):
    """Test updating a specific settings section"""
    # Setup a test instance
    instance_service.db.instances[test_instance_id] = MockInstance(
        test_instance_id, 
        default_settings
    )
    
    # Update behavior section
    behavior_settings = {
        "tone": "professional",
        "response_length": "concise",
        "greeting": "Welcome to our service!"
    }
    
    result = await instance_service.update_settings_section(
        test_instance_id,
        "behavior",
        behavior_settings
    )
    
    # Check that behavior section was updated
    assert result["settings"]["behavior"]["tone"] == "professional"
    assert result["settings"]["behavior"]["response_length"] == "concise"
    assert result["settings"]["behavior"]["greeting"] == "Welcome to our service!"
    
    # Check that other fields in behavior section remain unchanged
    assert "language" in result["settings"]["behavior"]
    
    # Check that other sections remain unchanged
    assert result["settings"]["identity"]["name"] == default_settings["identity"]["name"]


async def test_reset_settings(instance_service, test_instance_id):
    """Test resetting settings to default"""
    # Setup a test instance with modified settings
    custom_settings = get_default_settings()
    custom_settings["identity"]["name"] = "Custom Name"
    custom_settings["behavior"]["tone"] = "technical"
    
    instance_service.db.instances[test_instance_id] = MockInstance(
        test_instance_id, 
        custom_settings
    )
    
    # Reset settings
    result = await instance_service.reset_settings_to_default(test_instance_id)
    
    # Verify settings are reset to default
    assert result["settings"]["identity"]["name"] == "AI Assistant"
    assert result["settings"]["behavior"]["tone"] == "friendly"


def test_deep_merge_settings():
    """Test the deep merge functionality for settings"""
    instance_service = InstanceService(None)  # DB not needed for this test
    
    original = {
        "section1": {
            "key1": "value1",
            "key2": "value2",
            "nested": {
                "nested_key1": "nested_value1"
            }
        },
        "section2": {
            "key3": "value3"
        }
    }
    
    updates = {
        "section1": {
            "key2": "updated_value2",
            "nested": {
                "nested_key2": "nested_value2"
            }
        },
        "section3": {
            "key4": "value4"
        }
    }
    
    result = instance_service._deep_merge_settings(original, updates)
    
    # Check that the merge worked correctly
    assert result["section1"]["key1"] == "value1"
    assert result["section1"]["key2"] == "updated_value2"
    assert result["section1"]["nested"]["nested_key1"] == "nested_value1"
    assert result["section1"]["nested"]["nested_key2"] == "nested_value2"
    assert result["section2"]["key3"] == "value3"
    assert result["section3"]["key4"] == "value4"


def test_validate_settings():
    """Test settings validation"""
    # Valid settings should return empty error list
    valid_settings = {
        "identity": {
            "name": "Test Bot",
            "primary_color": "#FF5500"
        },
        "behavior": {
            "tone": "friendly"
        }
    }
    
    errors = validate_settings(valid_settings)
    assert len(errors) == 0
    
    # Invalid settings should return errors
    invalid_settings = {
        "identity": {
            "name": "Test Bot",
            "primary_color": "not-a-color"  # Invalid color format
        },
        "behavior": {
            "tone": "angry"  # Not a valid tone option
        }
    }
    
    errors = validate_settings(invalid_settings)
    assert len(errors) > 0 