from rest_framework import serializers

class ChatbotQuerySerializer(serializers.Serializer):
    query = serializers.CharField(
        max_length=1000,
        allow_blank=False,
        help_text="The question/query for the chatbot."
    )

class ChatbotResponseSerializer(serializers.Serializer):
    answer = serializers.CharField(read_only=True, help_text="The chatbot's answer.")
    query = serializers.CharField(read_only=True, help_text="The original query.") # Optional: echo back query

    def __init__(self, *args, **kwargs):
        # Allow 'query' to be passed for context but not as an input field for response creation
        original_query = kwargs.pop('original_query', None)
        super().__init__(*args, **kwargs)
        if original_query is not None:
            self.fields['query'].initial = original_query
