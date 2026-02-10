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
    # 1) 浏览器访问这个 URL 时，可能是两种情况：
    #    A. GET  请求：用户第一次打开“新建文章”页面 -> 需要显示一个空表单
    #    B. POST 请求：用户点击“保存/提交”按钮 -> 需要处理用户提交的数据

    if request.method == "POST":
        # 2) POST：说明用户点了提交按钮，浏览器把表单字段打包提交过来了
        # request.POST 是一个“字典一样”的对象，里面装的是用户填写的所有字段值
        form = PostForm(request.POST)

        # 3) 执行表单验证：
        #    - 字段类型是否正确（比如日期/整数）
        #    - 是否符合约束（max_length、required、空值等）
        if form.is_valid():
            # 4) form.save(commit=False) 的意思：
            #    - 根据表单数据“先生成一个 Post 对象”
            #    - 但先不要写入数据库（不执行 INSERT）
            #    因为我们还要补充一些表单里没有的字段，比如 author、publish_date
            post = form.save(commit=False)

            # 5) 给对象补上额外字段（这些字段不是用户输入的）
            post.author = request.user
            post.publish_date = timezone.now()

            # 6) 真正写入数据库：INSERT 新纪录
            post.save()

            # 7) 保存完成后跳转到详情页（避免刷新页面重复提交）
            return redirect("post_detail", pk=post.pk)

    else:
        # 1A) GET：用户第一次打开“新建文章”页面
        #     此时没有任何提交数据，所以创建一个空表单
        form = PostForm()

    # 8) 无论 GET 还是 POST（验证失败时），都渲染模板显示 form
    #    - GET：显示空表单
    #    - POST 验证失败：显示带错误信息的表单，用户可以修改再提交
    return render(request, "blog/post_edit.html", {"form": form})


def post_edit(request, pk):
    # 1) pk 是 URL 里带过来的文章主键，比如 /post/3/edit/
    #    先去数据库把这篇文章取出来，取不到就返回 404
    post = get_object_or_404(Post, pk=pk)

    # 2) 同样分 GET / POST 两种情况：
    #    A. GET：打开编辑页面 -> 显示“已存在文章的内容”作为默认值
    #    B. POST：提交保存 -> 用新数据更新这条文章

    if request.method == "POST":
        # 3) ⚠️ 关键点：instance=post
        #    这句的含义是：
        #    “这个表单对应的是数据库里已经存在的这条 post，
        #     我提交后要更新它，而不是新建一条”
        form = PostForm(request.POST, instance=post)

        # 4) 验证用户提交的数据是否合法
        if form.is_valid():
            # 5) commit=False：先得到“更新后的 post 对象”，但先不保存进数据库
            post = form.save(commit=False)

            # 6) 继续补充/覆盖一些不来自用户输入的字段
            post.author = request.user
            post.publish_date = timezone.now()

            # 7) 这里的 post.save() 会执行 UPDATE（更新）
            #    因为 post 已经有主键 pk，且 form 绑定了 instance
            post.save()

            # 8) 更新完成后跳转到详情页
            return redirect("post_detail", pk=post.pk)

    else:
        # 2A) GET：打开编辑页面
        #     instance=post 会把 post 现有字段值作为表单初始值显示出来
        form = PostForm(instance=post)

    # 9) 渲染模板：
    #    - GET：显示带默认值的表单
    #    - POST 验证失败：显示带错误信息的表单（用户填的内容也会保留）
    return render(request, "blog/post_edit.html", {"form": form})

@login_required
def post_edit_fragment(request, pk):
    """
    ✅ 原地编辑核心：
    - GET  ：返回“编辑态片段”（带表单，默认值来自 instance=post）
    - POST ：验证并保存，成功返回“展示态片段”；失败返回“带错误的编辑态片段”
    """
    # 1) 找到要编辑的那条 Post（找不到就 404）
    post = get_object_or_404(Post, pk=pk)

    # 2) 可选安全：只允许作者编辑
    #    如果你还没做 author 权限控制，建议先加上，防止别人编辑你的文章
    if post.author != request.user:
        return HttpResponse("Forbidden", status=403)

    if request.method == "POST":
        # 3) POST：用户点 Save，提交表单
        #    ✅ 关键：instance=post -> 更新这条记录（UPDATE），而不是新增（INSERT）
        form = PostForm(request.POST, instance=post)

        # 4) 校验表单字段（长度/必填/格式等）
        if form.is_valid():
            # 5) 先生成更新后的对象，但先不要保存到数据库
            post = form.save(commit=False)

            # 6) 补充表单里没有的字段（延续 DjangoGirls）
            post.author = request.user
            post.publish_date = timezone.now()

            # 7) 保存：因为有 instance，所以这里会 UPDATE
            post.save()

            # 8) 保存成功：返回展示态片段，前端会替换掉编辑表单
            return render(request, "blog/partials/post_display_fragment.html", {"post": post})

        # 9) 校验失败：返回编辑态片段（带错误信息），原地显示
        return render(request, "blog/partials/post_edit_fragment.html", {"form": form, "post": post})

    # 10) GET：用户点 ✎ Edit Post，进入编辑态
    form = PostForm(instance=post)
    return render(request, "blog/partials/post_edit_fragment.html", {"form": form, "post": post})


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
