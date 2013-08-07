# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
from django.db import models
from django.contrib.auth.models import User


class Book(models.Model):

    owner = models.ForeignKey(User)


class Color(models.Model):

    book = models.ForeignKey(Book)

    name = models.CharField(max_length=1024)
