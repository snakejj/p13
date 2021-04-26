from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.contrib import messages

from comments.models import *
from .forms import CommentForm


# Create your views here.


