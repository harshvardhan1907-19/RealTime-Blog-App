from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from .models import PasswordResetOTP, Post, Comment, Category, Notification, Profile
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
from .forms import *
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.db.models import Count
import random
import string
from datetime import datetime, timedelta
from django.core.mail import send_mail
from django.conf import settings

def generate_otp():
    """Generate 6-digit OTP"""
    return ''.join(random.choices(string.digits, k=6))

def forgot_password(request):
    """Step 1: Get email/username and send OTP"""
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email_or_username = form.cleaned_data['email_or_username']
            
            # Find user by email or username
            try:
                if '@' in email_or_username:
                    user = User.objects.get(email=email_or_username)
                else:
                    user = User.objects.get(username=email_or_username)
            except User.DoesNotExist:
                messages.error(request, 'No account found with this email/username')
                return render(request, 'blog/forgot_password.html', {'form': form})
            
            # Generate and save OTP
            otp = generate_otp()
            PasswordResetOTP.objects.create(user=user, otp=otp)
            
            # Send OTP via email (if user has email)
            if user.email:
                try:
                    send_mail(
                        subject='Password Reset OTP - BlogApp',
                        message=f'Hello {user.username},\n\nYour OTP for password reset is: {otp}\n\nThis OTP is valid for 10 minutes.\n\nIf you did not request this, please ignore this email.\n\nThanks,\nBlogApp Team',
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[user.email],
                        fail_silently=False,
                    )
                    messages.success(request, f'OTP sent to {user.email}')
                except Exception as e:
                    print(f"Email error: {e}")
                    messages.warning(request, f'OTP generated but email could not be sent. Use this OTP: {otp}')
            else:
                messages.warning(request, f'No email registered. Use this OTP: {otp}')
            
            # Store user_id in session for next steps
            request.session['reset_user_id'] = user.id
            return redirect('verify_otp')
    else:
        form = ForgotPasswordForm()
    
    return render(request, 'blog/forgot_password.html', {'form': form})

def verify_otp(request):
    """Step 2: Verify OTP"""
    user_id = request.session.get('reset_user_id')
    
    if not user_id:
        messages.error(request, 'Session expired. Please start over.')
        return redirect('forgot_password')
    
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        messages.error(request, 'User not found')
        return redirect('forgot_password')
    
    if request.method == 'POST':
        form = VerifyOtpForm(request.POST)
        if form.is_valid():
            otp = form.cleaned_data['otp']
            
            try:
                otp_record = PasswordResetOTP.objects.get(user=user, otp=otp, is_used=False)
                
                if otp_record.is_valid():
                    # Mark OTP as used
                    otp_record.is_used = True
                    otp_record.save()
                    
                    messages.success(request, 'OTP verified! Set your new password.')
                    print("Exiting from otp verification")
                    return redirect('set_new_password')
                else:
                    messages.error(request, 'OTP has expired. Please request a new one.')
                    return redirect('forgot_password')
            except PasswordResetOTP.DoesNotExist:
                messages.error(request, 'Invalid OTP. Please try again.')
    else:
        form = VerifyOtpForm()
    
    return render(request, 'blog/verify_otp.html', {'form': form, 'email': user.email})

def set_new_password(request):
    """Step 3: Set new password"""
    print("Entering into set password function")
    user_id = request.session.get('reset_user_id')
    
    if not user_id:
        messages.error(request, 'Session expired. Please start over.')
        return redirect('forgot_password')
    
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        messages.error(request, 'User not found')
        return redirect('forgot_password')
    
    if request.method == 'POST':
        print("Processing new password form submission")
        form = SetNewPasswordForm(request.POST)
        if form.is_valid():
            new_password = form.cleaned_data['new_password1']
            user.set_password(new_password)
            user.save()
            print("Done")
            
            # Clear session
            del request.session['reset_user_id']
            
            print("Wait process")
            messages.success(request, 'Password reset successfully! Please login with your new password.')
            print("✅ Password reset successful for user:", user.username)
            return redirect('login')
        else:
            print("❌ FORM VALIDATION FAILED:", form.errors)
    else:
        form = SetNewPasswordForm()
    
    return render(request, 'blog/set_new_password.html', {'form': form})

@login_required
def profile_view(request, username=None):

    if username:
        user = get_object_or_404(User, username=username)
    else:
        user = request.user

    profile, created = Profile.objects.get_or_create(user=user)

    user_posts = Post.objects.filter(author=user)
    liked_posts = user.liked_posts.all()
    print("Total followers", profile.followers.count())

    total_posts = user_posts.count()
    total_likes = sum(post.total_likes() for post in user_posts)
    total_views = sum(post.views for post in user_posts)

    is_following = False
    if request.user.is_authenticated and request.user != user:
        is_following = profile.followers.filter(id=request.user.id).exists()

    context = {
        'user': user,
        'profile': profile,
        'user_posts': user_posts,
        'liked_posts': liked_posts,
        'total_posts': total_posts,
        'total_likes': total_likes,
        'total_views': total_views,
        'is_following': is_following,
    }

    return render(request, "blog/profile.html", context)

@login_required
def profile_update(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    # profile   The Profile object (existing OR newly created)	<Profile: harsh's Profile>
    # created   Boolean: True if NEW, False if EXISTING	        True or False

    if request.method == "POST":
        form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = ProfileUpdateForm(instance=profile)

    return render(request, 'blog/profile_update.html', {'form':form, 'profile':profile})

@login_required
def delete_profile_pic(request):
    profile = request.user.profile
    
    try:
        if profile.profile_pic:
            # Delete the file
            profile.profile_pic.delete(save=False)
            # Clear the field
            profile.profile_pic = None
            profile.save()
    except Exception as e:
        # If file doesn't exist, just clear the field
        profile.profile_pic = None
        profile.save()
    
    return redirect('profile')

def change_password(request):
    if request.method == "POST":
        form = PasswordChange(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            # This keeps the user logged in after the password change
            messages.success(request, "Your password has been successfully updated!")
            update_session_auth_hash(request, user)
            return redirect("post_list")
    else:
        form = PasswordChange(user=request.user)

    return render(request, "blog/password_change.html", {"form":form})

def register(request):
    if request.method == "POST":
        form = CustomeUserCreation(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created successfully! Please login.')
            return redirect("login")
    else:
        form = CustomeUserCreation()
    
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

            print(f"✅ Sent like notification with ID: {notification.id}")

    return JsonResponse({
        'liked': liked,
        'total_likes': post.likes.count()
    })

@login_required
def follow_user(request, username):
    user_to_follow = get_object_or_404(User, username=username)
    
    if request.user == user_to_follow:
        return JsonResponse({'error': 'You cannot follow yourself'}, status=400)
    
    # ✅ Get or create profile for the user to follow
    profile_to_follow, created = Profile.objects.get_or_create(user=user_to_follow)
    
    # ✅ Add current user to followers (User object, not Profile)
    profile_to_follow.followers.add(request.user)
    
    return JsonResponse({
        'success': True,
        'action': 'follow',
        'followers_count': profile_to_follow.followers.count()
    })

@login_required
def unfollow_user(request, username):
    try:
        user_to_unfollow = get_object_or_404(User, username=username)
        
        # if request.user == user_to_unfollow:
        #     return JsonResponse({'error': 'You cannot unfollow yourself'}, status=400)
        
        # ✅ Get the profile
        profile_to_unfollow = user_to_unfollow.profile
        
        # ✅ Remove current user from followers
        profile_to_unfollow.followers.remove(request.user)
        
        return JsonResponse({
            'success': True,
            'action': 'unfollow',
            'followers_count': profile_to_unfollow.followers.count()
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def check_follow_status(request, username):
    user_to_check = get_object_or_404(User, username=username)
    
    # ✅ Check if current user is in the followers list
    is_following = user_to_check.profile.followers.filter(id=request.user.id).exists()
    
    return JsonResponse({
        'is_following': is_following,
        'followers_count': user_to_check.profile.followers.count()
    })

class PostCreateView(LoginRequiredMixin, CreateView):
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
        sorted_by = self.request.GET.get('sort', '-created_at')

        if query:
            # queryset = queryset.filter(title__icontains=query) | queryset.filter(content__icontains=query)
            queryset = queryset.filter(
                Q(title__icontains=query) | Q(content__icontains=query)
            )

        if category:
            queryset = queryset.filter(category__id=category)
        
        if sorted_by == "-likes":
            queryset = queryset.annotate(like_count=Count('likes')).order_by("-like_count")
        elif sorted_by == "-views":
            queryset = queryset.order_by("-views")
        else:
            queryset = queryset.order_by("-created_at")
        
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
        sorted_by = request.GET.get('sort', '-created_at')

        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) | Q(content__icontains=query)
            )

        if category and category != "":
            queryset = queryset.filter(category__id=int(category))

        if sorted_by == "-likes":
            # annotate() -> Adds a temporary calculated field to each object
            # like_count -> The name of the temporary field (you can name it anything)
            # Count('likes') -> Counts how many related likes objects each post ha
            queryset = queryset.annotate(like_count=Count('likes')).order_by("-like_count")
                # SELECT
                #     post.*, 
                #     COUNT(likes.id) AS like_count
                # FROM post
                # LEFT JOIN likes ON post.id = likes.post_id
                # GROUP BY post.id
        elif sorted_by == "-views":
            queryset = queryset.order_by("-views")
        else:
            queryset = queryset.order_by("-created_at")

        paginator = Paginator(queryset, 4)
        page_obj = paginator.get_page(page)

        html = render_to_string("blog/post_list_partial_modern.html", {
            "posts": page_obj
        }, request=request)
        print("COUNT:", queryset.count())
        return JsonResponse({"html": html, "has_next": page_obj.has_next()})

class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/post_detail.html'

    def get_context_data(self, **kwargs): # Send extra data from view → template
        context = super().get_context_data(**kwargs) # 👉 Context = dictionary that sends data from view → template /// Parent class = DetailView
        # def get_context_data(self, **kwargs):
        # return {
        #     'object': self.object
        # }
        context['comments'] = Comment.objects.filter(post=self.object, parent__isnull=True).order_by('-created_at')
        return context
    
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

        # increment view count
        self.object.views += 1
        self.object.save()

        context = self.get_context_data(object = self.object)
        return self.render_to_response(context)
    
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        text = request.POST.get("text")
        parent_id = request.POST.get("parent_id")

        if request.user.is_authenticated and text:
            parent = None
            # reply_to = None

            if parent_id:
                parent_comment = Comment.objects.get(id=parent_id)
                parent = parent_comment

            comment = Comment.objects.create(
                post = self.object,
                user = request.user,
                text = text,
                parent = parent,
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

            html = render_to_string("blog/reply_modern.html", {
                "comment": comment,
                "request": request,
                "depth": 1 if parent else 0,
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

def handler404(request, exception):
    return render(request, '404.html', status=404)

def handler500(request):
    return render(request, '500.html', status=500)
