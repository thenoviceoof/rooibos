from threading import Thread
from django.db import models
from django.db.models import Q
from django.db.models.signals import post_delete, post_save
from django.contrib.contenttypes.models import ContentType
from rooibos.data.models import Record, Collection, Field, FieldValue, CollectionItem
from rooibos.storage.models import Media
from rooibos.contrib.tagging.models import TaggedItem
from rooibos.util.models import OwnedWrapper
from django.conf import settings
from . import SolrIndex
from pysolr import Solr
import logging


class SolrIndexUpdates(models.Model):
    record = models.IntegerField()
    delete = models.BooleanField(default=False)


def mark_for_update(record_id, delete=False):
    SolrIndexUpdates.objects.create(record=record_id, delete=delete)

def post_record_delete_callback(sender, **kwargs):
    mark_for_update(record_id=kwargs['instance'].id, delete=True)

def post_record_save_callback(sender, **kwargs):
    mark_for_update(record_id=kwargs['instance'].id)

def post_taggeditem_callback(sender, instance, **kwargs):
    if instance and instance.content_type == ContentType.objects.get_for_model(OwnedWrapper):
        instance = instance.object
        if instance and instance.content_type == ContentType.objects.get_for_model(Record):
            mark_for_update(record_id=instance.object_id)


def post_collectionitem_save_callback(sender, **kwargs):
    mark_for_update(record_id=kwargs['instance'].record_id)

def post_collectionitem_delete_callback(sender, **kwargs):
    mark_for_update(record_id=kwargs['instance'].record_id, delete=True)


post_delete.connect(post_record_delete_callback, sender=Record)
post_save.connect(post_record_save_callback, sender=Record)

post_delete.connect(post_taggeditem_callback, sender=TaggedItem)
post_save.connect(post_taggeditem_callback, sender=TaggedItem)

post_delete.connect(post_collectionitem_delete_callback, sender=CollectionItem)
post_save.connect(post_collectionitem_save_callback, sender=CollectionItem)


def disconnect_signals():
    post_delete.disconnect(post_record_delete_callback, sender=Record)
    post_save.disconnect(post_record_save_callback, sender=Record)

    post_delete.disconnect(post_taggeditem_callback, sender=TaggedItem)
    post_save.disconnect(post_taggeditem_callback, sender=TaggedItem)

    post_delete.disconnect(post_collectionitem_callback, sender=CollectionItem)
    post_save.disconnect(post_collectionitem_callback, sender=CollectionItem)
