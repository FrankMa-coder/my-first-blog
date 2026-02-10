from django import forms
from .models import Post


class PostForm(forms.ModelForm):
    """
    PostForm：用于新建/编辑 Post 的表单。
    我们通过 widgets 给字段加上更现代的 UI 属性：
    - class="form-control"：套用 Bootstrap 表单样式
    - placeholder：占位提示
    - rows：让 textarea 初始更舒适
    """

    class Meta:
        model = Post
        fields = ("title", "text")
        widgets = {
            "title": forms.TextInput(
                attrs={
                    # ✅ Bootstrap：输入框样式
                    "class": "form-control form-control-lg",
                    # ✅ 体验：提示文案
                    "placeholder": "Give your post a clear title…",
                    # ✅ 让浏览器不要自动乱填
                    "autocomplete": "off",
                }
            ),
            "text": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Write something thoughtful…",
                    "rows": 12,
                }
            ),
        }

        # ✅ 可选：如果你想自定义 label 文案
        labels = {
            "title": "Title",
            "text": "Text",
        }
