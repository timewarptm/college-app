from django.db import models
from django.utils.translation import gettext_lazy as _

class FAQEntry(models.Model):
    question_text = models.TextField(
        _("question text"),
        help_text=_("The common way a question is asked.")
    )
    answer_text = models.TextField(
        _("answer text"),
        help_text=_("The answer to be provided for the question.")
    )
    keywords = models.CharField(
        _("keywords"),
        max_length=255,
        blank=True,
        help_text=_("Comma-separated keywords for matching queries. E.g., 'fees,payment,tuition'.")
    )
    category = models.CharField(
        _("category"),
        max_length=100,
        blank=True,
        null=True,
        help_text=_("Optional category for organizing FAQs. E.g., 'Admissions', 'Technical Support'.")
    )
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    def __str__(self):
        return self.question_text[:100] # Display first 100 chars of question

    class Meta:
        verbose_name = _("FAQ Entry")
        verbose_name_plural = _("FAQ Entries")
        ordering = ['category', 'question_text']
