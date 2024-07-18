from django.shortcuts import render


def test(request):
    data = {
        'settings': {
            'title_suffix': 'DEBUG',
        },
        'page': {
            'title': 'Test Page',
            'title_seo': 'SEO Test Page',
            'description': 'This is a test page.',
        },
        'content': 'Martin Lanser',
        'news': [
            'First news item',
            'Second news item',
            'Third news item',
            'Fourth news item',
        ],
    }

    return render(request, 'test.html', data)
