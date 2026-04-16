from django.urls import path
from .views import book_list, get_chat_history, save_chat, upload_book, ask_question

urlpatterns = [
    path('books/', book_list, name='book_list'),
    path('upload/', upload_book, name='upload_book'),
    path('ask/', ask_question, name='ask_question'),
     path('chat/save/', save_chat),
    path('chat/history/', get_chat_history),
]