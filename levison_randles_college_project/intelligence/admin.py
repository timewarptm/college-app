from django.contrib import admin
from .models import FAQEntry

@admin.register(FAQEntry)
class FAQEntryAdmin(admin.ModelAdmin):
    list_display = ('question_text_preview', 'category', 'keywords_display', 'created_at', 'updated_at')
    list_filter = ('category', 'created_at')
    search_fields = ('question_text', 'answer_text', 'keywords', 'category')
    fields = ('question_text', 'answer_text', 'keywords', 'category') # Layout for edit form

    def question_text_preview(self, obj):
        return (obj.question_text[:75] + '...') if len(obj.question_text) > 75 else obj.question_text
    question_text_preview.short_description = "Question Preview"

    def keywords_display(self, obj):
        return obj.keywords if obj.keywords else "-"
    keywords_display.short_description = "Keywords"
