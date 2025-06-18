from .models import FAQEntry
import re

class FAQChatbotService:
    DEFAULT_NO_ANSWER_RESPONSE = "I'm sorry, I don't have an answer for that right now. Please try asking in a different way or contact support."

    def get_response(self, query: str) -> str:
        normalized_query = query.lower().strip()
        if not normalized_query:
            return "Please ask a question."

        # 1. Try direct match (case-insensitive) on question_text
        # Using `iexact` for case-insensitive exact match
        direct_match = FAQEntry.objects.filter(question_text__iexact=normalized_query).first()
        if direct_match:
            return direct_match.answer_text

        # 2. Try partial match on question_text (e.g., if query is a substring of a question)
        # This can be broad, so use with caution or refine.
        # For example, if a stored question is "How do I reset my password?" and query is "reset password",
        # `icontains` would match.
        partial_match_questions = FAQEntry.objects.filter(question_text__icontains=normalized_query)
        if partial_match_questions.exists():
            # If multiple partial matches, could return the first, or try to rank them.
            # For simplicity, return the first one.
            return partial_match_questions.first().answer_text


        # 3. Keyword-based matching
        query_words = set(re.split(r'\W+', normalized_query)) # Split by non-alphanumeric characters

        # Fetch all FAQs to iterate for keyword matching if no direct/partial match found
        # This could be inefficient for very large FAQ sets.
        # Consider optimizing if performance becomes an issue (e.g., pre-indexing keywords).
        all_faqs = FAQEntry.objects.all()

        best_keyword_match_faq = None
        max_keyword_overlap = 0

        for faq in all_faqs:
            if not faq.keywords:
                continue

            faq_keywords = set(k.strip().lower() for k in faq.keywords.split(',') if k.strip())
            overlap = len(query_words.intersection(faq_keywords))

            if overlap > max_keyword_overlap:
                max_keyword_overlap = overlap
                best_keyword_match_faq = faq
            elif overlap > 0 and overlap == max_keyword_overlap:
                # Simple tie-breaking: prefer shorter keyword lists or more specific entries if possible.
                # For now, just takes the first one encountered with max_overlap.
                pass

        if best_keyword_match_faq and max_keyword_overlap > 0:
            # Could have a threshold for min_keyword_overlap to be considered a valid match
            return best_keyword_match_faq.answer_text

        return self.DEFAULT_NO_ANSWER_RESPONSE
