"""
Feature flags system for safe experimentation.

Enables enabling/disabling features at runtime without code changes.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
from enum import Enum

from config.settings import settings

logger = logging.getLogger(__name__)


class Feature(str, Enum):
    """Feature flag names."""
    REAL_WEB_SEARCH = "FEATURE_REAL_WEB_SEARCH"
    REAL_IMAGE_GENERATION = "FEATURE_REAL_IMAGE_GENERATION"
    PERSISTENT_LEARNING = "FEATURE_PERSISTENT_LEARNING"
    DISTRIBUTED_TRACING = "FEATURE_DISTRIBUTED_TRACING"


class FeatureFlags:
    """
    Feature flags management system.

    Enables/disables features at runtime with optional conditions.
    """

    def __init__(self):
        """Initialize feature flags from settings."""
        self._flags: Dict[str, bool] = {
            Feature.REAL_WEB_SEARCH: settings.FEATURE_REAL_WEB_SEARCH,
            Feature.REAL_IMAGE_GENERATION: settings.FEATURE_REAL_IMAGE_GENERATION,
            Feature.PERSISTENT_LEARNING: settings.FEATURE_PERSISTENT_LEARNING,
            Feature.DISTRIBUTED_TRACING: settings.FEATURE_DISTRIBUTED_TRACING,
        }
        self._metadata: Dict[str, Dict[str, Any]] = {}
        logger.info("Feature flags initialized")
        self._log_features()

    def is_enabled(self, feature: Feature) -> bool:
        """
        Check if a feature is enabled.

        Args:
            feature: Feature to check

        Returns:
            True if enabled, False otherwise
        """
        enabled = self._flags.get(feature.value, False)
        if not enabled:
            logger.debug(f"Feature {feature.value} is disabled")
        return enabled

    def enable(self, feature: Feature, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Enable a feature.

        Args:
            feature: Feature to enable
            metadata: Optional metadata about the feature
        """
        self._flags[feature.value] = True
        if metadata:
            self._metadata[feature.value] = {
                **metadata,
                "enabled_at": datetime.utcnow().isoformat(),
            }
        logger.info(f"Feature {feature.value} enabled")

    def disable(self, feature: Feature) -> None:
        """
        Disable a feature.

        Args:
            feature: Feature to disable
        """
        self._flags[feature.value] = False
        if feature.value in self._metadata:
            self._metadata[feature.value]["disabled_at"] = datetime.utcnow().isoformat()
        logger.info(f"Feature {feature.value} disabled")

    def toggle(self, feature: Feature) -> bool:
        """
        Toggle a feature on/off.

        Args:
            feature: Feature to toggle

        Returns:
            New state of the feature
        """
        new_state = not self._flags.get(feature.value, False)
        self._flags[feature.value] = new_state
        logger.info(f"Feature {feature.value} toggled to {new_state}")
        return new_state

    def get_metadata(self, feature: Feature) -> Dict[str, Any]:
        """
        Get metadata for a feature.

        Args:
            feature: Feature to get metadata for

        Returns:
            Feature metadata or empty dict
        """
        return self._metadata.get(feature.value, {})

    def get_all_flags(self) -> Dict[str, bool]:
        """Get all feature flags."""
        return self._flags.copy()

    def get_enabled_features(self) -> list:
        """Get list of enabled features."""
        return [feature for feature, enabled in self._flags.items() if enabled]

    def get_disabled_features(self) -> list:
        """Get list of disabled features."""
        return [feature for feature, enabled in self._flags.items() if not enabled]

    def _log_features(self) -> None:
        """Log current feature flags."""
        enabled = self.get_enabled_features()
        disabled = self.get_disabled_features()
        logger.info(f"Enabled features: {enabled}")
        logger.info(f"Disabled features: {disabled}")


# Global feature flags instance
_feature_flags = None


def get_feature_flags() -> FeatureFlags:
    """Get the global feature flags instance."""
    global _feature_flags
    if _feature_flags is None:
        _feature_flags = FeatureFlags()
    return _feature_flags


def is_feature_enabled(feature: Feature) -> bool:
    """
    Check if a feature is enabled (convenience function).

    Args:
        feature: Feature to check

    Returns:
        True if enabled, False otherwise

    Example:
        >>> from core.feature_flags import Feature, is_feature_enabled
        >>> if is_feature_enabled(Feature.REAL_WEB_SEARCH):
        ...     # Use real web search
        ...     pass
    """
    return get_feature_flags().is_enabled(feature)
