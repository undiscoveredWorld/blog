from django.http import HttpResponse
from django.template import loader


# Create your views here.
def list_posts(request):
    template = loader.get_template('posts/list.html')
    return HttpResponse(template.render({}, request))
