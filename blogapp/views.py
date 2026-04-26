from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Post, Comment, Category, Notification
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin 
from django.contrib.auth.forms import UserCreationForm 
from django.db.models import Q
# Purpose: Complex database queries (OR conditions for search)
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .serializer import PostSerializer
from rest_framework import status, viewsets
from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string
from django.core import serializers
from django.core.paginator import Paginator
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST

def register(request):
    if request.method == "POST":
        
        form = UserCreationForm(request.POST)
        for field in form.fields.values():
            field.widget.attrs['class'] = "form-control"
        
        if form.is_valid():
            form.save()
            return redirect("login")
    else:
        form = UserCreationForm()
        for field in form.fields.values():
            field.widget.attrs['class'] = 'form-control'
    
    return render(request, 'register.html', {"form": form})

@login_required
def like_post(request, pk):
    post = get_object_or_404(Post, id=pk)

    if request.user in post.likes.all():
        post.likes.remove(request.user)
        liked = False
    else:
        post.likes.add(request.user)
        liked = True

        if post.author != request.user:
            notification = Notification.objects.create(
                user=post.author,
                sender=request.user,
                post=post,
                message=f"{request.user.username} liked your post"
            )

            channel_layer = get_channel_layer()

            async_to_sync(channel_layer.group_send)(
                f"user_{post.author.id}",
                {
                    "type": "send_notification",
                    "notification_id": notification.id,  # ← MUST HAVE THIS LINE
                    "message": notification.message,
                    "post_id": post.id,
                    "comment_id": None
                }
            )

            print(f"✅ Sent like notification with ID: {notification.id}")  # ← Add this debug

    return JsonResponse({
        'liked': liked,
        'total_likes': post.likes.count()
    })

@login_required
def profile_view(request):
    user = request.user

    user_posts = Post.objects.filter(author=user)
    liked_posts = user.liked_posts.all()

    total_posts = user_posts.count()

    # total likes received on your posts
    total_likes = sum(post.total_likes() for post in user_posts)

    context = {
        'user': user,
        'user_posts': user_posts,
        'liked_posts': liked_posts,
        'total_posts': total_posts,
        'total_likes': total_likes
    }

    return render(request, "blog/profile.html", context)

class PostCreateView(CreateView):
    model = Post
    fields = ['title', 'content', 'category', 'image']
    template_name = "blog/post_form.html"
    success_url = reverse_lazy('post_list')

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)

        for field in form.fields.values():
            field.widget.attrs['class'] = 'form-control'
            form.fields['content'].widget.attrs.update({
                'class': 'form-control',
                'rows': 5
            })

        return form

class PostListView(ListView):
    model = Post
    template_name = 'blog/post_list.html'
    context_object_name = 'posts'
    ordering = ['-created_at']
    paginate_by = 4

    def get_queryset(self):
        queryset = Post.objects.all()
        query = self.request.GET.get("q")
        category = self.request.GET.get('category')

        if query:
            # queryset = queryset.filter(title__icontains=query) | queryset.filter(content__icontains=query)
            queryset = queryset.filter(
                Q(title__icontains=query) | Q(content__icontains=query)
            )

        if category:
            queryset = queryset.filter(category__id=category)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()

        if self.request.user.is_authenticated:
            context['notification_count'] = Notification.objects.filter(
                user = self.request.user,
                is_read = False
            ).count()
        else:
            context['notification_count'] = 0
        return context
    
def filter_posts(request):
        queryset = Post.objects.all()

        query = request.GET.get("q") # getting filter value from url
        category = request.GET.get('category')
        page = request.GET.get("page", 1)

        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) | Q(content__icontains=query)
            )

        if category and category != "":
            queryset = queryset.filter(category__id=int(category))

        paginator = Paginator(queryset, 4)
        page_obj = paginator.get_page(page)

        html = render_to_string("blog/post_list_partial.html", {
            "posts": page_obj
        }, request=request)
        print("COUNT:", queryset.count())
        return JsonResponse({"html": html, "has_next": page_obj.has_next()})

class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/post_detail.html'

    def get_context_data(self, **kwargs): # Send extra data from view → template
        context = super().get_context_data(**kwargs) # 👉 Context = dictionary that sends data from view → template ////// Parent class = DetailView
        # def get_context_data(self, **kwargs):
        # return {
        #     'object': self.object
        # }
        context['comments'] = Comment.objects.filter(post=self.object, parent__isnull=True).order_by('-created_at')
        return context
    
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        text = request.POST.get("text")
        parent_id = request.POST.get("parent_id")

        if request.user.is_authenticated and text:
            parent = None

            if parent_id:
                parent = Comment.objects.get(id=parent_id)

            comment = Comment.objects.create(
                post = self.object,
                user = request.user,
                text = text,
                parent = parent
            )

            channel_layer = get_channel_layer()

            if parent is None and self.object.author != request.user:
                print("🎯 Entering MAIN COMMENT notification block")
                notification = Notification.objects.create(
                    user = self.object.author,
                    sender = request.user,
                    post = self.object,
                    comment = comment,
                    message = f"{request.user.username} commented on your post"
                )

                try:    
                    async_to_sync(channel_layer.group_send)(
                        f"user_{self.object.author.id}",
                        {
                            "type": "send_notification",
                            "notification_id": notification.id,
                            "message": notification.message,
                            "post_id": self.object.id,
                            "comment_id": comment.id
                        }
                    )
                except Exception as e:
                    print(f"❌ WebSocket send FAILED: {e}")

            if parent and parent.user != request.user:
                print("🎯 Entering REPLY notification block")
                notification = Notification.objects.create(
                    user = parent.user,
                    sender = request.user,
                    post = self.object,
                    comment = comment,
                    message = f"{request.user.username} replied to your comment"
                )

                print(f"📝 Database notification created with ID: {notification.id}")
                print(f"📤 Attempting to send WebSocket to group: user_{parent.user.id}")

                try:
                    async_to_sync(channel_layer.group_send) (
                        f"user_{parent.user.id}",
                        {
                            "type": "send_notification",
                            "notification_id": notification.id,
                            "message": notification.message,
                            "post_id": self.object.id,
                            "comment_id": comment.id
                        }
                    )
                    print(f"📨 WebSocket reply notification sent to user {parent.user.id}")
                except Exception as e:
                    print(f"❌ WebSocket send FAILED: {e}")

            html = render_to_string("blog/reply.html", {
                "comment": comment,
                "request": request,
                "depth": 1 if parent else 0
            })

            return JsonResponse({"html": html})
        
        print("❌ Comment not saved - user not authenticated or no text")
        return JsonResponse({"error": "Invalid"}, status=400)
        # return redirect("post_detail", pk=self.object.pk)

@login_required
def notification_view(request):
    notifications = Notification.objects.filter(user=request.user).order_by("-created_at")

    # make all as read
    notifications.update(is_read=True)
    
    return render(request, "blog/notification.html", {
        'notifications': notifications
    })

@login_required
def get_notifications(request):
    notifications = Notification.objects.filter(user=request.user, is_read=False).order_by("-created_at")[:5]

    data = []
    for n in notifications:
        data.append({
            'id': n.id,
            'message': n.message,
            'time': n.created_at.strftime("%d %b %H:%M"),
            'post_id': n.post.id if n.post else None,
            'comment_id': n.comment.id if n.comment else None
        })
    
    return JsonResponse({'notifications': data})

@login_required
def notification_count_api(request):
    count = Notification.objects.filter(
        user=request.user,
        is_read=False
    ).count()

    return JsonResponse({"count": count})

@login_required
def mark_notification_read(request, pk):
    notif = Notification.objects.get(id=pk, user=request.user)
    notif.is_read = True
    notif.save()
    # print(Notification.objects).count()
    count = Notification.objects.filter(
        user=request.user,
        is_read=False
    ).count()
    return JsonResponse({'success': True, 'count': count})
    
class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    fields = ['title', 'content', 'category', 'image']
    template_name = "blog/post_form.html"
    success_url = reverse_lazy("post_list")

    def get_queryset(self):
        return Post.objects.filter(author=self.request.user)
    
    def form_valid(self, form):
        old_post = self.get_object()

        if old_post.image:
            if 'image' in form.changed_data:
                old_post.image.delete(save=False)

        return super().form_valid(form)  
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)

        for field in form.fields.values():
            field.widget.attrs['class'] = 'form-control'
            form.fields['content'].widget.attrs.update({
            'class': 'form-control',
            'rows': 5
        })

        return form
    
class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = "blog/post_confirm_delete.html"
    success_url = reverse_lazy("post_list")

    def get_queryset(self):
        return Post.objects.filter(author=self.request.user)


# API => FBV

@api_view(["GET"])
def api_post_list(request):
    posts = Post.objects.all()
    serializer = PostSerializer(posts, many=True)
    return Response(serializer.data)

@api_view(["GET"])
def api_post_detail(request, pk):
    try:
        post = Post.objects.get(pk=pk)
    except:
        return Response(status=status.HTTP_404_NOT_FOUND)
    # if request.method == "GET":
    serializer = PostSerializer(post)
    return Response(serializer.data)

@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def api_post_update(request, pk):
    try:
        post = Post.objects.get(pk=pk)
    except:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    if post.author != request.user:
        return Response({"error": "Not allowed"}, status=403)
    
    serializer = PostSerializer(post, data = request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def api_post_delete(request, pk):
    try:
        post = Post.objects.get(pk=pk)
    except:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    if post.author != request.user:
        return Response({"error": "Not allowed"}, status=403)
    
    post.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def api_post_form(request):
    serializer = PostSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save(author=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# API => CBV
class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]


    def get_queryset(self):
        queryset =  Post.objects.all().order_by("-created_at")

        query = self.request.GET.get('q')
        category = self.request.GET.get("category")

        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) | Q(category__name__icontains=query)
            )

        if category:
            queryset = queryset.filter(category__id=category)

        return queryset
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)