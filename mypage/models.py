
from django.shortcuts import render, redirect
from common.models import User
from django.contrib import messages
from .forms import ProfileUpdateForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash