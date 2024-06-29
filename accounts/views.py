from django.conf import settings
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render

from accounts.models import CustomUser


def user_profile(request, userID):
    user = get_object_or_404(CustomUser, id=userID)

    data = {
        'user': user,
    }

    return render(request, 'user_profile.html', data)


def user_list(request):
    users = CustomUser.objects.all().order_by('user_name')
    paginator = Paginator(users, settings.DEFAULT_LIST_LEN)

    pageNum = int(request.GET.get('page', 1))
    page = paginator.page(max(min(pageNum, paginator.num_pages), 1))

    data = {
        'users': page.object_list,
        'page': page,
    }

    return render(request, 'user_list.html', data)
