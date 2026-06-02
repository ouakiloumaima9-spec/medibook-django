from django.contrib import messages
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from doctors.models import Doctor
from .ai_engine import engine


@require_http_methods(['GET', 'POST'])
def orient(request):
    motif = ''
    results = []
    if request.method == 'POST':
        motif = request.POST.get('motif', '').strip()
        if len(motif) < 5:
            messages.warning(request, 'Veuillez saisir un motif un peu plus précis.')
        else:
            suggestions = engine.predict(motif, top_k=3)
            for suggestion in suggestions:
                doctors = Doctor.objects.filter(
                    specialties=suggestion['specialty'],
                    is_active=True,
                ).select_related('user').prefetch_related('specialties')[:3]
                results.append({
                    'specialty': suggestion['specialty'],
                    'score': suggestion['score'],
                    'doctors': doctors,
                })
    return render(request, 'ai_orientation/orient.html', {'motif': motif, 'results': results})
