from django.shortcuts import render, get_object_or_404
from .models import Post
from django.utils import timezone
from .forms import PostForm
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.urls import reverse


# Create your views here.
def post_list(request):
    posts = Post.objects.filter(publish_date__lte=timezone.now()).order_by(
        "-publish_date"
    )
    # The last parameter, {}, is a place in which we can add some things for the template to use.
    return render(request, "blog/post_list.html", {"posts": posts})


def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    return render(request, "blog/post_detail.html", {"post": post})


def post_new(request):

    if request.method == "POST":
        form = PostForm(request.POST)

        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            action = request.POST.get("action")
            if action == "publish":
                post.publish_date = timezone.now()
            else:
                post.publish_date = None
            post.save()
            return redirect("post_detail", pk=post.pk)
    else:
        form = PostForm()

    return render(request, "blog/post_edit.html", {"form": form})


def post_edit(request, pk):

    post = get_object_or_404(Post, pk=pk)

    if request.method == "POST":
        form = PostForm(request.POST, instance=post)

        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.publish_date = timezone.now()

            post.save()

            return redirect("post_detail", pk=post.pk)

    else:
        form = PostForm(instance=post)
    return render(request, "blog/post_edit.html", {"form": form})


@login_required
def post_edit_fragment(request, pk):
  
    post = get_object_or_404(Post, pk=pk)

    if post.author != request.user:
        return HttpResponse("Forbidden", status=403)

    if request.method == "POST":
     
        form = PostForm(request.POST, instance=post)

        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            action = request.POST.get("action")
            if action == "save":
                post.publish_date = timezone.now()
            else:
                post.publish_date = None
           
            post.save()
            return render(
                request, "blog/partials/post_display_fragment.html", {"post": post}
            )

        return render(
            request,
            "blog/partials/post_edit_fragment.html",
            {"form": form, "post": post},
        )

    form = PostForm(instance=post)
    return render(
        request, "blog/partials/post_edit_fragment.html", {"form": form, "post": post}
    )


@login_required
def post_cancel_fragment(request, pk):
    """
    ✅ 退出编辑（Exit）：
    - 不保存，直接返回展示态片段
    """
    post = get_object_or_404(Post, pk=pk)

    # 同样建议做权限控制
    if post.author != request.user:
        return HttpResponse("Forbidden", status=403)

    return render(request, "blog/partials/post_display_fragment.html", {"post": post})


@login_required
def post_delete(request, pk):
    """
    ✅ 删除文章（Delete）：
    - 只允许 POST（避免 GET 一点就删的危险）
    - 删除成功后回主页 post_list
    - 如果是 HTMX 请求：用 HX-Redirect 触发“整页跳转”
    """
    post = get_object_or_404(Post, pk=pk)

    # 权限控制：只允许作者删除
    if post.author != request.user:
        return HttpResponse("Forbidden", status=403)

    if request.method != "POST":
        # 非 POST 一律拒绝（更安全）
        return HttpResponse("Method Not Allowed", status=405)

    # 1) 删除（数据库 DELETE）
    post.delete()

    # 2) 删除后要回主页
    home_url = reverse("post_list")

    # 3) 判断是否为 HTMX 请求（HTMX 会带 HX-Request: true）
    is_htmx = request.headers.get("HX-Request") == "true"

    if is_htmx:
        # ✅ HTMX 专用：用 HX-Redirect 让浏览器整页跳转到主页
        response = HttpResponse(status=204)  # 204: No Content（不需要返回 HTML）
        response["HX-Redirect"] = home_url
        return response

    # 4) 普通请求：用 Django redirect
    return redirect("post_list")


def post_draft_list(request):
    posts = Post.objects.filter(publish_date__isnull=True).order_by("-created_date")
    return render(request, "blog/post_draft_list.html", {"posts": posts})


def post_publish(request, pk):
    post = get_object_or_404(Post, pk=pk)

    if request.method == "POST":
        post.publish()
        print(post)
    return redirect("post_detail", pk=pk)
