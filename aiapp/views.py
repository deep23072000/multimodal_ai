import wikipedia
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib import messages

from .forms import UploadForm
from .models import SearchHistory


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

        # === Handle uploaded image ===
        if request.FILES.get('image'):
            image_file = request.FILES['image']
            results.append({
                'title': '📷 Uploaded Image',
                'description': f'Image file "{image_file.name}" received. (Hook up to CLIP/BLIP here)'
            })

        # === Handle uploaded audio ===
        if request.FILES.get('audio'):
            audio_file = request.FILES['audio']
            results.append({
                'title': '🎤 Uploaded Audio',
                'description': f'Audio file "{audio_file.name}" received. (Hook up to Whisper here)'
            })

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

    # Treat this as if it's a result
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
