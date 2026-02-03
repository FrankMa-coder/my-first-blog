from django.shortcuts import render
from .models import Post
from django.utils import timezone

# Create your views here.
def post_list(request):
    posts = Post.objects.filter(publish_date__lte=timezone.now()).order_by('publish_date')
    # The last parameter, {}, is a place in which we can add some things for the template to use. 
    return render(request, 'blog/post_list.html', {'posts':posts})