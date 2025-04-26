from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Post

class StaticSitemap(Sitemap):
    def items(self):
        return ["index"]
    def location(self, item):
        return reverse(item)
class PostSitemap(Sitemap):
    def items(self):
        return Post.objects.all()[:100]