from typing import Dict, List, Optional, Literal, Union
from pydantic import BaseModel, Field, HttpUrl


class IdentitySettings(BaseModel):
    """Identity and branding settings for an instance."""
    name: str = Field(default="AI Assistant")
    description: str = Field(default="Your AI assistant to help with website navigation and tasks.")
    logo_url: Optional[str] = None
    primary_color: str = Field(default="#3B82F6")  # Default blue color
    secondary_color: Optional[str] = None
    accent_color: Optional[str] = None


class WebsiteCrawlingSettings(BaseModel):
    """Settings for website crawling functionality."""
    enabled: bool = Field(default=True)
    depth: int = Field(default=2, ge=1, le=5)
    include_patterns: List[str] = Field(default_factory=list)
    exclude_patterns: List[str] = Field(default_factory=lambda: ["*/admin*", "*/login*"])
    frequency: Literal["daily", "weekly", "monthly", "manual"] = Field(default="weekly")
    require_authentication: bool = Field(default=False)


class ManualKnowledgeSettings(BaseModel):
    """Settings for manual knowledge sources."""
    enable_document_upload: bool = Field(default=True)
    enable_faq_builder: bool = Field(default=True)
    enable_knowledge_snippets: bool = Field(default=True)


class LearningSettings(BaseModel):
    """Settings for agent learning capabilities."""
    enable_learning_from_interactions: bool = Field(default=True)
    require_admin_review: bool = Field(default=True)
    feedback_collection: bool = Field(default=True)


class KnowledgeSettings(BaseModel):
    """Knowledge acquisition and management settings."""
    crawling: WebsiteCrawlingSettings = Field(default_factory=WebsiteCrawlingSettings)
    manual_sources: ManualKnowledgeSettings = Field(default_factory=ManualKnowledgeSettings)
    learning: LearningSettings = Field(default_factory=LearningSettings)


class BehaviorSettings(BaseModel):
    """Agent behavior and communication settings."""
    tone: Literal["professional", "friendly", "technical", "casual"] = Field(default="friendly")
    response_length: Literal["concise", "balanced", "detailed"] = Field(default="balanced")
    language: str = Field(default="en")
    greeting: str = Field(default="Hello! I'm your AI assistant. How can I help you today?")
    fallback_message: str = Field(
        default="I'm not sure I understand. Could you please rephrase your question or request?"
    )
    proactivity_level: Literal["low", "medium", "high"] = Field(default="medium")


class ElementPermissionSettings(BaseModel):
    """Permission settings for DOM element interactions."""
    buttons: bool = Field(default=True)
    forms: bool = Field(default=True)
    links: bool = Field(default=True)
    inputs: bool = Field(default=True)
    file_uploads: bool = Field(default=False)  # More sensitive, off by default


class InteractionSettings(BaseModel):
    """Website interaction capabilities settings."""
    global_permission_level: Literal["read-only", "guided", "full"] = Field(default="guided")
    element_permissions: ElementPermissionSettings = Field(default_factory=ElementPermissionSettings)
    protected_selectors: List[str] = Field(default_factory=list)
    require_confirmation: bool = Field(default=True)
    highlight_color: str = Field(default="#3B82F6")
    highlight_animation: bool = Field(default=True)
    interaction_speed: Literal["slow", "medium", "fast"] = Field(default="medium")


class WidgetSettings(BaseModel):
    """Chat widget appearance settings."""
    position: Literal["bottom-right", "bottom-left", "top-right", "top-left"] = Field(default="bottom-right")
    size: Literal["small", "medium", "large"] = Field(default="medium")
    theme: Literal["light", "dark", "auto"] = Field(default="light")
    show_branding: bool = Field(default=True)
    custom_css: Optional[str] = None
    bubble_icon_url: Optional[str] = None
    mobile_position: Literal["bottom", "top"] = Field(default="bottom")


class DeploymentSettings(BaseModel):
    """Widget deployment and integration settings."""
    initialization: Literal["immediate", "delayed", "on-scroll", "on-exit-intent"] = Field(default="delayed")
    excluded_paths: List[str] = Field(default_factory=list)
    included_paths: List[str] = Field(default_factory=list)
    show_on_mobile: bool = Field(default=True)


class IntegrationSettings(BaseModel):
    """External integrations configuration."""
    crm_webhook_url: Optional[str] = None
    analytics_enabled: bool = Field(default=True)
    enable_ticketing: bool = Field(default=False)
    email_notifications: bool = Field(default=False)
    deployment: DeploymentSettings = Field(default_factory=DeploymentSettings)


class ComplianceSettings(BaseModel):
    """Data handling and compliance settings."""
    data_retention_days: int = Field(default=90, ge=1, le=365)
    detect_pii: bool = Field(default=True)
    mask_pii: bool = Field(default=True)
    gdpr_compliance: bool = Field(default=True)
    ccpa_compliance: bool = Field(default=True)
    require_consent: bool = Field(default=True)


class InstanceSettings(BaseModel):
    """Complete settings structure for an AI Agent instance."""
    version: str = Field(default="1.0")
    identity: IdentitySettings = Field(default_factory=IdentitySettings)
    knowledge: KnowledgeSettings = Field(default_factory=KnowledgeSettings)
    behavior: BehaviorSettings = Field(default_factory=BehaviorSettings)
    interaction: InteractionSettings = Field(default_factory=InteractionSettings)
    appearance: WidgetSettings = Field(default_factory=WidgetSettings)
    integration: IntegrationSettings = Field(default_factory=IntegrationSettings)
    compliance: ComplianceSettings = Field(default_factory=ComplianceSettings)

    class Config:
        use_enum_values = True


def get_default_settings() -> Dict:
    """Return the default settings for a new instance."""
    return InstanceSettings().dict() 