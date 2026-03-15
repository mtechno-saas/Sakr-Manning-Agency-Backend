from django.contrib import admin

# ai_agents/admin.py

from .models import (
    ChatSession, 
    ChatMessage, 
    SearchQuery, 
    PopularSearch, 
    UserPreference, 
    ConversationContext
)

@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ['session_id', 'user', 'title', 'total_messages', 'created_at', 'is_active']
    list_filter = ['is_active', 'created_at', 'last_activity']
    search_fields = ['session_id', 'title', 'user__username']
    readonly_fields = ['session_id', 'created_at', 'updated_at']
    ordering = ['-updated_at']

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['session', 'role', 'content_preview', 'search_type', 'timestamp', 'response_time']
    list_filter = ['role', 'search_type', 'timestamp']
    search_fields = ['content', 'session__session_id']
    readonly_fields = ['timestamp']
    ordering = ['-timestamp']
    
    def content_preview(self, obj):
        return obj.content[:100] + "..." if len(obj.content) > 100 else obj.content
    content_preview.short_description = 'Content Preview'

@admin.register(SearchQuery)
class SearchQueryAdmin(admin.ModelAdmin):
    list_display = ['query_preview', 'user', 'search_type', 'results_found', 'response_time', 'timestamp']
    list_filter = ['search_type', 'results_found', 'timestamp']
    search_fields = ['query', 'user__username']
    readonly_fields = ['timestamp']
    ordering = ['-timestamp']
    
    def query_preview(self, obj):
        return obj.query[:50] + "..." if len(obj.query) > 50 else obj.query
    query_preview.short_description = 'Query Preview'

@admin.register(PopularSearch)
class PopularSearchAdmin(admin.ModelAdmin):
    list_display = ['topic', 'search_count', 'last_searched']
    list_filter = ['last_searched']
    search_fields = ['topic']
    ordering = ['-search_count', '-last_searched']

@admin.register(UserPreference)
class UserPreferenceAdmin(admin.ModelAdmin):
    list_display = ['user', 'preferred_search_depth', 'enable_follow_up_suggestions', 'language_preference']
    list_filter = ['preferred_search_depth', 'enable_follow_up_suggestions', 'language_preference']
    search_fields = ['user__username']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(ConversationContext)
class ConversationContextAdmin(admin.ModelAdmin):
    list_display = ['session', 'topics_preview', 'last_updated']
    search_fields = ['session__session_id', 'conversation_summary']
    readonly_fields = ['last_updated']
    ordering = ['-last_updated']
    
    def topics_preview(self, obj):
        topics = obj.current_topics[:3] if obj.current_topics else []
        return ", ".join(topics) if topics else "No topics"
    topics_preview.short_description = 'Current Topics'