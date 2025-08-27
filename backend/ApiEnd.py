# your_app/management/commands/list_api_endpoints.py
from django.core.management.base import BaseCommand
from django.urls import get_resolver
from django.conf import settings
import re

class Command(BaseCommand):
    help = 'List all API endpoints'

    def add_arguments(self, parser):
        parser.add_argument(
            '--format',
            type=str,
            default='table',
            choices=['table', 'json'],
            help='Output format (table or json)'
        )

    def handle(self, *args, **options):
        def collect_urls(resolver, prefix=''):
            urls = []
            for pattern in resolver.url_patterns:
                if hasattr(pattern, 'resolve'):
                    # It's a URL pattern
                    if hasattr(pattern, 'callback'):
                        view_name = pattern.callback.__name__
                        view_class = getattr(pattern.callback, 'view_class', None)
                        if view_class:
                            view_name = view_class.__name__
                        
                        # Extract HTTP methods if it's a DRF ViewSet or APIView
                        methods = []
                        if hasattr(pattern.callback, 'view_class'):
                            view_class = pattern.callback.view_class
                            if hasattr(view_class, 'http_method_names'):
                                methods = [m.upper() for m in view_class.http_method_names if m != 'options']
                            elif hasattr(view_class, 'allowed_methods'):
                                methods = list(view_class.allowed_methods)
                        
                        if not methods:
                            methods = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']
                        
                        url_pattern = prefix + str(pattern.pattern)
                        # Clean up the URL pattern
                        url_pattern = re.sub(r'\^|\$', '', url_pattern)
                        
                        urls.append({
                            'url': url_pattern,
                            'view': view_name,
                            'methods': methods,
                        })
                elif hasattr(pattern, 'url_patterns'):
                    # It's an include, recurse
                    nested_prefix = prefix + str(pattern.pattern).replace('^', '').replace('$', '')
                    urls.extend(collect_urls(pattern, nested_prefix))
            return urls

        resolver = get_resolver()
        all_urls = collect_urls(resolver)
        
        # Filter for API endpoints (you can customize this filter)
        api_urls = [url for url in all_urls if 'api' in url['url'].lower()]
        
        if options['format'] == 'json':
            import json
            self.stdout.write(json.dumps(api_urls, indent=2))
        else:
            # Table format
            self.stdout.write(self.style.SUCCESS('API Endpoints:'))
            self.stdout.write('-' * 80)
            self.stdout.write(f"{'URL':<40} {'Methods':<20} {'View':<20}")
            self.stdout.write('-' * 80)
            
            for url in api_urls:
                methods_str = ', '.join(url['methods'][:3])  # Show first 3 methods
                if len(url['methods']) > 3:
                    methods_str += '...'
                
                self.stdout.write(f"{url['url']:<40} {methods_str:<20} {url['view']:<20}")
            
            self.stdout.write('-' * 80)
            self.stdout.write(f"Total API endpoints: {len(api_urls)}")