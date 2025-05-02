from django.urls import path
from .views import FeedView, TweetCreateView

urlpatterns = [
    path("feed/", FeedView.as_view()),
    path("tweets/", TweetCreateView.as_view()),
]
