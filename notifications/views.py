from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def notifications_list(request):
    notifications = request.user.notifications.all()
    request.user.notifications.filter(is_read=False).update(is_read=True)
    return render(request, 'notifications/list.html', {'notifications': notifications})
