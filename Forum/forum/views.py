from django.shortcuts import render

from django.views.generic import (
    CreateView,
    DetailView,
    ListView,
    FormView
    )
from .forms import My_chat_botForm
from .models import Forum, Comment
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy, reverse
from .my_chat_bot import MyChatBot
from django.core import serializers
# Create your views here.


class ForumDetailView(LoginRequiredMixin, FormView):
    template_name = 'forum/forum_detail.html'
    form_class = My_chat_botForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["Forum"] = Forum.objects.get(id=self.kwargs['pk'])
        context["Comment_List"] = Comment.objects.filter(forum_id=self.kwargs['pk'])
        return context
    
    def get_success_url(self):
        return reverse('forum-detail', kwargs={'pk':self.kwargs['pk']})

    def form_valid(self, form):
        message = form.send_message()
        #response = MyChatBot("名無し:", message)
        comment = Comment(user=self.request.user, text=message, forum=Forum.objects.get(id=self.kwargs['pk']))
        comment.save()
        data = serializers.serialize('json', [comment])
        return super().form_valid(form)

    

    
class ForumListView(LoginRequiredMixin, ListView):
    template_name = "forum/forum_list.html"
    model = Forum

class ForumCreateView(LoginRequiredMixin, CreateView):
    template_name = "forum/forum_create.html"
    model = Forum
    success_url = reverse_lazy("forum-list")
    fields = ("title",)
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)



