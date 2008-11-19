from tango.models import *
from django.contrib import admin

class TapeAdmin(admin.ModelAdmin):
    list_display = ('title', 'subtitle', 'duration_pretty')
    prepopulated_fields = {'slug':('title', 'subtitle',)}

class TrackAdmin(admin.ModelAdmin):
    list_display = ('tape', 'track_num', 'title', 'artist', 'duration_pretty')
    fieldsets = (
            (None, {
                'fields': ('tape', 'file',)
            }), 
            ('Track info', {
                'classes': ('collapse'), 
                'fields': ('artist', 'title',)
            })
    )

admin.site.register(Tape, TapeAdmin)
admin.site.register(Track, TrackAdmin)
