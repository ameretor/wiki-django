from re import L
import re
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.utils import html
import markdown as md
from . import util
from django import forms
from django.contrib import messages
from django.urls import reverse
import random


class SearchForm(forms.Form):
    """ Form Class for Search Bar """
    title = forms.CharField(label="", widget=forms.TextInput(attrs={
        "class": "search",
        "placeholder": "Search this Wiki"
    }))


class CreateForm(forms.Form):
    """ Form class for create new entries"""
    title = forms.CharField(label="", widget=forms.TextInput(attrs={
        "class": "form-control",
        "id": "exampleFormControlInput1",
        "placeholder": "Title of entry",
    }))

    content = forms.CharField(label="Your content", widget=forms.Textarea(attrs={
        "placeholder": "Enter entry content",
        "class": "form-control",
        "id": "exampleFormControlTextArea1"
    }))


class EditForm(forms.Form):
    """Form class for editing existed entries"""
    content = forms.CharField(label="", widget=forms.Textarea(attrs={
        "class": "form-control",
        "id": "exampleFormControlTextArea1",
        "placeholder": "Enter text here"
    }))


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries(),
        "search_form": SearchForm()
    })


def entry(request, title):
    """Displays requested Documentation """
    md_entry = util.get_entry(title)

    if md_entry is None:
        return render(request, "encyclopedia/error.html", {
            "title": title
        })
    # Convert markdown entries into HTML
    html_entry = md.markdown(md_entry)
    return render(request, "encyclopedia/entry.html", {
        "title": title,
        "entry": html_entry,
        "search_form": SearchForm()
    })


def search(request):
    """ Display searched requests """
    if request.method != "POST":
        return render(request, "encyclopedia/index.html", {
            "entries": util.list_entries(),
            "search_form": SearchForm()
        })
    form = SearchForm(request.POST)

    if form.is_valid():
        title = form.cleaned_data["title"]
        md_entry = util.get_entry(title)

        print("User searched: ", title)

        if md_entry:
            return redirect(reverse('entry', args=[title]))
        else:
            return render(request, "encyclopedia/search.html", {
                "search_form": SearchForm(),
                "title": title,
                "related_title": related_title(title)
            })


def related_title(title):
    """ Return all titles related to search terms """
    real_entry = list(util.list_entries())
    return [
        entry
        for entry in real_entry
        if title.lower() in entry.lower() or entry.lower() in title.lower()
    ]


def create(request):

    if request.method == "POST":

        form = CreateForm(request.POST)

        if form.is_valid():
            # Validate data
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]

            if not util.get_entry(title):
                util.save_entry(title, content)
                messages.success(
                    request, f"Successfully put '{title}' in our encyclopedia. Thank you!")
                return redirect(reverse('entry', args=[title]))
            else:
                messages.error(
                    request, "This entry is already there. What you doing? Please check it out!")
                return render(request, "encyclopedia/create.html", {
                    "create_form": CreateForm(),
                    "search_form": SearchForm()
                })

        else:
            messages.error(
                request, "Your entry was not valid, please double check!")
            return render(request, "encyclopedia/create.html", {
                "create_form": CreateForm(),
            })

    return render(request, "encyclopedia/create.html", {
        "create_form": CreateForm(),
        "search_form": SearchForm()
    })


def edit(request, title):
    """ Edit existing entries"""
    if request.method == "GET":

        content = util.get_entry(title)
        # Check if entry existed
        if content is None:
            messages.error(
                request, f"'{title}' Entry is not there. Maybe you want to create new one?")

        # Edit entry
        return render(request, "encyclopedia/edit.html", {
            "title": title,
            "edit_form": EditForm(initial={
                "content": content
            }),
            "search_form": SearchForm()
        })
    if request.method == "POST":

        form = EditForm(request.POST)

        if form.is_valid():

            content = form.cleaned_data["content"]
            util.save_entry(title, content)
            messages.success(
                request, f"Successfully editted '{title}'. Thank you!")
            return redirect(reverse('entry', args=[title]))

        else:
            messages.error(request, "Edit failed. Please try again")
            return render(request, "encyclopedia/edit.html", {
                "title": title,
                "edit_form": form,
                "search_form": SearchForm()
            })


def random_entry(request):
    """Display random title"""
    # Get all entries
    all_entries = util.list_entries()
    # Get a random title
    title = random.choice(all_entries)

    return redirect(reverse('entry', args=[title]))
