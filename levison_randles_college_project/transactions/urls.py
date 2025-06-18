from django.urls import path
from .views import GiveTipView, SentTipsListView, ReceivedTipsListView

urlpatterns = [
    path('tips/give/', GiveTipView.as_view(), name='give_tip'),
    path('tips/sent/', SentTipsListView.as_view(), name='list_sent_tips'),
    path('tips/received/', ReceivedTipsListView.as_view(), name='list_received_tips'),
]
