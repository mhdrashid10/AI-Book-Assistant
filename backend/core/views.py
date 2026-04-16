from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from core.scraper import scrape_books
from .models import Book
from .serializers import BookSerializer
from .rag_utils import process_book, rag_query
from .models import Book, ChatHistory


@api_view(['GET'])
def book_list(request):
    books = Book.objects.all()
    serializer = BookSerializer(books, many=True)
    return Response(serializer.data)


@api_view(['POST'])
def upload_book(request):
    data = request.data

    book = Book.objects.create(
        title=data.get('title'),
        author=data.get('author', 'Unknown Author'),
        description=data.get('description', '')
    )

    process_book(book)

    return Response({"message": "Book processed", "id": str(book.id)})

@api_view(['POST'])
def save_chat(request):
    question = request.data.get('question')
    answer = request.data.get('answer')
    sources = request.data.get('sources', '')
    
    if question and answer:
        ChatHistory.objects.create(
            question=question,
            answer=answer,
            sources=str(sources)
        )
    return Response({"status": "saved"})


@api_view(['GET'])
def get_chat_history(request):
    history = ChatHistory.objects.all().order_by('-created_at')[:20]
    data = [{
        'id': str(h.id),
        'question': h.question,
        'answer': h.answer,
        'sources': h.sources,
        'time': h.created_at.strftime("%Y-%m-%d %H:%M")
    } for h in history]
    return Response(data)

@api_view(['POST'])
def ask_question(request):
    question = request.data.get('question')

    if not question:
        return Response({"error": "Question required"}, status=400)

    result = rag_query(question)
    return Response(result)

@api_view(['POST'])
def trigger_scrape(request):
    pages = int(request.data.get('pages', 3))   # Allow choosing number of pages
    count = scrape_books(pages=pages)
    return Response({"message": f"Successfully scraped {count} books from {pages} pages!"})