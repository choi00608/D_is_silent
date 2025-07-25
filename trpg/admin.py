from django.contrib import admin
from django.utils.html import format_html
from .models import Player, GameScenario, GameSession, GameLog

@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

@admin.register(GameScenario)
class GameScenarioAdmin(admin.ModelAdmin):
    list_display = ('title', 'description')

@admin.register(GameSession)
class GameSessionAdmin(admin.ModelAdmin):
    list_display = ('id', 'scenario', 'player', 'created_at')
    list_filter = ('scenario', 'player')

@admin.register(GameLog)
class GameLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'session', 'display_message', 'is_sent_by_user', 'is_major_decision', 'timestamp')
    list_filter = ('session', 'is_major_decision', 'is_sent_by_user')
    search_fields = ('message',)

    def display_message(self, obj):
        # If the message is short, just display it.
        if len(obj.message) <= 100:
            return obj.message
        
        # If it's long, create a toggleable view
        short_version = obj.message[:100] + '...'
        full_version = obj.message
        log_id = obj.id

        return format_html(
            '''
            <div id="short_msg_{0}">{1}</div>
            <div id="full_msg_{0}" style="display:none;">{2}</div>
            <a id="toggle_link_{0}" href="javascript:void(0);" onclick="toggle_message({0})">[전체 보기]</a>
            ''',
            log_id,
            short_version,
            full_version
        )
    
    display_message.short_description = "Message"

    # Include custom JavaScript in the admin page
    class Media:
        js = ('admin/js/log_toggle.js',)
