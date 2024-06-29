from django.shortcuts import render


def test(request):
    data = {
        'content': 'Martin Lanser',
        'news': [
            'First news item',
            'Second news item',
            'Third news item',
            'Fourth news item',
        ],
    }

    return render(request, 'test.html', data)


def news(request):
    data = {
        'news': [
            'First news item',
            'Second news item',
            'Third news item',
            'Fourth news item',
        ]
    }

    return render(request, 'news.html', data)
