from django.db import models

# Create your models here.
# ai_agents/models.py
from django.db import models
from django.conf import settings
import uuid
from django.utils import timezone

class ChatSession(models.Model):
    """
    Represents a chat session between a user and the AI agent.
    """
    session_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='chat_sessions'
    )
    title = models.CharField(max_length=200, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_activity = models.DateTimeField(default=timezone.now)
    total_messages = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['user', '-updated_at']),
            models.Index(fields=['session_id']),
        ]
    
    def __str__(self):
        return f"Session {self.session_id} - {self.title or 'Untitled'}"


class ChatMessage(models.Model):
    """
    Individual messages within a chat session.
    """
    ROLE_CHOICES = [
        ('user', 'User'),
        ('assistant', 'Assistant'),
        ('system', 'System'),
    ]
    
    SEARCH_TYPE_CHOICES = [
        ('general', 'General Search'),
        ('news', 'News Search'),
        ('research', 'Research Search'),
        ('fact_check', 'Fact Check'),
        ('conversational', 'Conversational Search'),
    ]
    
    session = models.ForeignKey(
        ChatSession, 
        on_delete=models.CASCADE, 
        related_name='messages'
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    search_type = models.CharField(
        max_length=20, 
        choices=SEARCH_TYPE_CHOICES, 
        default='general'
    )
    tools_used = models.JSONField(default=list, blank=True)
    response_time = models.FloatField(null=True, blank=True)
    
    class Meta:
        ordering = ['timestamp']
        indexes = [
            models.Index(fields=['session', 'timestamp']),
            models.Index(fields=['role', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.role}: {self.content[:50]}..."


class SearchQuery(models.Model):
    """
    Track search queries for analytics and improvements.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='search_queries'
    )
    session = models.ForeignKey(
        ChatSession, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='search_queries'
    )
    query = models.TextField()
    search_type = models.CharField(max_length=50)
    tools_used = models.JSONField(default=list)
    results_found = models.BooleanField(default=True)
    response_time = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['search_type', '-timestamp']),
        ]
    
    def __str__(self):
        return f"Query: {self.query[:50]}..."


class PopularSearch(models.Model):
    """
    Track popular search topics for recommendations.
    """
    topic = models.CharField(max_length=200, unique=True)
    search_count = models.IntegerField(default=1)
    last_searched = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-search_count', '-last_searched']
    
    def __str__(self):
        return f"{self.topic} ({self.search_count} searches)"


class UserPreference(models.Model):
    """
    Store user preferences for personalized search experience.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='search_preferences'
    )
    preferred_search_depth = models.CharField(
        max_length=20,
        choices=[
            ('basic', 'Basic'),
            ('medium', 'Medium'),
            ('comprehensive', 'Comprehensive'),
        ],
        default='medium'
    )
    enable_follow_up_suggestions = models.BooleanField(default=True)
    preferred_sources = models.JSONField(default=list, blank=True)
    language_preference = models.CharField(max_length=10, default='en')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Preferences for {self.user}"


class ConversationContext(models.Model):
    """
    Store conversation context for better continuity.
    """
    session = models.OneToOneField(
        ChatSession, 
        on_delete=models.CASCADE,
        related_name='context'
    )
    current_topics = models.JSONField(default=list)
    user_interests = models.JSONField(default=list)
    conversation_summary = models.TextField(blank=True)
    last_updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Context for {self.session}"

class QueryCache(models.Model):
    """
    Cache for Text-to-SQL RAG queries.
    """
    question = models.TextField(unique=True)
    sql_query = models.TextField()
    final_answer = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cached Query: {self.question[:50]}"

class FailedQueryLog(models.Model):
    """
    Log for failed Text-to-SQL queries to improve the system.
    """
    question = models.TextField()
    generated_sql = models.TextField()
    error_message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Failed Query: {self.question[:50]}"