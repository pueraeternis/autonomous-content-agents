"""Backward-compatible Twitter client re-export."""

from content_agents.services.publishers.twitter import TwitterPublisher

TwitterClient = TwitterPublisher

# Singleton instance for backward compatibility
twitter_service = TwitterPublisher()

__all__ = ["TwitterClient", "TwitterPublisher", "twitter_service"]
