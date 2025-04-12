import wikipedia
import tempfile
import os

from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib import messages

from .forms import UploadForm
from .models import SearchHistory
from .ml_utils import classify_image  # ⬅️ Import the ML utility

from .whisper_transcribe import transcribe_audio


def paginate_history(request, history_queryset, per_page=5):
    paginator = Paginator(history_queryset, per_page)
    page_number = request.GET.get("page")
    return paginator.get_page(page_number)


def home(request):
    results = []
    form = UploadForm(request.POST or None, request.FILES or None)

    if request.method == "POST" and form.is_valid():
        query = form.cleaned_data.get('query')

        # === Handle text query (Wikipedia) ===
        if query:
            try:
                page = wikipedia.page(query)
                description = page.content[:500] + '...'
                results.append({
                    'title': page.title,
                    'description': description
                })

                # Save to search history
                SearchHistory.objects.create(
                    query=query,
                    title=page.title,
                    description=description
                )

            except wikipedia.exceptions.DisambiguationError as e:
                description = f'Ambiguous query: {", ".join(e.options[:5])}...'
                results.append({
                    'title': 'Disambiguation Error',
                    'description': description
                })

                SearchHistory.objects.create(
                    query=query,
                    title="Disambiguation Error",
                    description=description
                )

            except wikipedia.exceptions.PageError:
                description = 'No Wikipedia page found for your query.'
                results.append({
                    'title': 'Page Not Found',
                    'description': description
                })

                SearchHistory.objects.create(
                    query=query,
                    title="Page Not Found",
                    description=description
                )

        # === Handle uploaded image and run ML prediction ===
        if request.FILES.get('image'):
            image_file = request.FILES['image']
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
                for chunk in image_file.chunks():
                    tmp.write(chunk)
                tmp_path = tmp.name

            predictions = classify_image(tmp_path)
            os.unlink(tmp_path)  # 🔥 Clean up temp file

            pred_text = "\n".join([f"{i+1}. {label} ({prob:.2%})" for i, (label, prob) in enumerate(predictions)])

            results.append({
                'title': f'📷 Image: {image_file.name}',
                'description': pred_text
            })

            SearchHistory.objects.create(
                query=f"Image: {image_file.name}",
                title="Image Classification",
                description=pred_text
            )

        # === Handle uploaded audio ===
        if request.FILES.get('audio'):
            audio_file = request.FILES['audio']
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
                for chunk in audio_file.chunks():
                    tmp.write(chunk)
            tmp_path = tmp.name

    # Run transcription using Whisper
            transcription = transcribe_audio(tmp_path)
            os.unlink(tmp_path)

            results.append({
                'title': '🎤 Audio Transcription',
                'description': transcription
            })

            SearchHistory.objects.create(
                query=f"Audio: {audio_file.name}",
                title="Audio Transcription",
                description=transcription
             )

    # Fetch and paginate all search history
    history_queryset = SearchHistory.objects.order_by('-timestamp')
    history_page = paginate_history(request, history_queryset)

    return render(request, 'aiapp/multimodal_search.html', {
        'form': form,
        'results': results,
        'history': history_page,
    })


def history_detail(request, pk):
    item = get_object_or_404(SearchHistory, pk=pk)

    results = [{
        'title': item.title,
        'description': item.description,
    }]

    form = UploadForm()  # empty form on detail page

    history_queryset = SearchHistory.objects.order_by('-timestamp')
    history_page = paginate_history(request, history_queryset)

    return render(request, 'aiapp/multimodal_search.html', {
        'form': form,
        'results': results,
        'history': history_page,
    })


def clear_history(request):
    if request.method == "POST":
        SearchHistory.objects.all().delete()
        messages.success(request, "History cleared successfully.")
    return redirect('home')


def delete_history(request, pk):
    if request.method == "POST":
        item = get_object_or_404(SearchHistory, pk=pk)
        item.delete()
        messages.success(request, f'History item "{item.title}" deleted.')
    return redirect('home')
