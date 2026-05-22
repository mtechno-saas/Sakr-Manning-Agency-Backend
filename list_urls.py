import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "saker.settings")
django.setup()

from django.urls import get_resolver

def show_urls(patterns, prefix=''):
    for pattern in patterns:
        if hasattr(pattern, 'url_patterns'):
            show_urls(pattern.url_patterns, prefix + str(pattern.pattern))
        else:
            print(f"{prefix}{str(pattern.pattern)}")

resolver = get_resolver()
show_urls(resolver.url_patterns)
