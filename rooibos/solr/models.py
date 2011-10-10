from threading import Thread
from django.db import models
from django.db.models import Q
from django.db.models.signals import post_delete, post_save
from django.contrib.contenttypes.models import ContentType
from rooibos.data.models import Record, Collection, Field, FieldValue, CollectionItem
from rooibos.storage.models import Media
from rooibos.contrib.tagging.models import TaggedItem
from rooibos.util.models import OwnedWrapper
from pysolr import Solr


class SolrIndexUpdates(models.Model):
    record = models.IntegerField()
    delete = models.BooleanField(default=False)


def mark_for_update(record_id, delete=False):
    SolrIndexUpdates.objects.create(record=record_id, delete=delete)


def post_record_delete_callback(sender, **kwargs):
    mark_for_update(record_id=kwargs['instance'].id, delete=True)

def post_record_save_callback(sender, **kwargs):
    mark_for_update(record_id=kwargs['instance'].id)

    ###
    # _record_type = int(ContentType.objects.get_for_model(Record).id)

    # parent_groups = {}
    # def _build_group_tree():
    #     parent_groups = {}
    #     for collection in Collection.objects.all():
    #         parent_groups[collection.id] = [g.id for g in collection.all_parent_collections]
    # _build_group_tree()

    # def _preload_related(model, record_ids, filter=Q(), related=0):
    #     dict = {}
    #     for x in model.objects.select_related(depth=related).filter(filter, record__id__in=record_ids):
    #         dict.setdefault(x.record_id, []).append(x)
    #     return dict

    # def _clean_string(s):
    #     """Cleanse string of various control characters"""
    #     _clean_string_re = re.compile('[\x00-\x08\x0b\x0c\x0e-\x1f]')
    #     return _clean_string_re.sub(' ', s)

    # def _determine_resolution_label(width, height):
    #     sizes = ((2400, 'large'), (1600, 'moderate'), (800, 'medium'), (400, 'small'),)
    #     r = max(width, height)
    #     if not r: return 'unknown'
    #     for s, t in sizes:
    #         if r >= s: return t
    #     return 'tiny'

    # def _record_to_solr(record, core_fields, groups, fieldvalues, media):
    #     required_fields = dict((f.name, None) for f in core_fields.keys())
    #     doc = { 'id': str(record.id) }
    #     for v in fieldvalues:
    #         clean_value = _clean_string(v.value)
    #         # Store Dublin Core or equivalent field for use with facets
    #         for cf, cfe in core_fields.iteritems():
    #             if v.field == cf or v.field in cfe:
    #                 doc.setdefault(cf.name + '_t', []).append(clean_value)
    #                 if not doc.has_key(cf.name + '_sort'):
    #                     doc[cf.name + '_sort'] = clean_value
    #                 required_fields.pop(cf.name, None)
    #                 break
    #         else:
    #             doc.setdefault(v.field.name + '_t', []).append(clean_value)
    #         # For exact retrieval through browsing
    #         doc.setdefault(v.field.full_name + '_s', []).append(clean_value)
    #     for f in required_fields:
    #         doc[f + '_t'] = SOLR_EMPTY_FIELD_VALUE
    #     all_parents = [g.collection_id for g in groups]
    #     parents = [g.collection_id for g in groups if not g.hidden]
    #     # Combine the direct parents with (great-)grandparents
    #     doc['collections'] = list(reduce(lambda x, y: set(x) | set(y), [parent_groups[p] for p in parents], parents))
    #     doc['allcollections'] = list(reduce(lambda x, y: set(x) | set(y), [parent_groups[p] for p in all_parents], all_parents))
    #     doc['presentations'] = record.presentationitem_set.all().distinct().values_list('presentation_id', flat=True)
    #     if record.owner_id:
    #         doc['owner'] = record.owner_id
    #     for m in media:
    #         doc.setdefault('mimetype', []).append('s%s-%s' % (m.storage_id, m.mimetype))
    #         doc.setdefault('resolution', []).append('s%s-%s' % (m.storage_id, _determine_resolution_label(m.width, m.height)))
    #     # Index tags
    #     for ownedwrapper in OwnedWrapper.objects.select_related('user').filter(content_type=self._record_type, object_id=record.id):
    #         for tag in ownedwrapper.taggeditem.select_related('tag').all().values_list('tag__name', flat=True):
    #             doc.setdefault('tag', []).append(tag)
    #             doc.setdefault('ownedtag', []).append('%s-%s' % (ownedwrapper.user.id, tag))
    #     return doc

    # def process_data(groups, fieldvalues, media):
    #     def process():
    #         docs = []
    #         for record in Record.objects.filter(id__in=record_ids):
    #             docs += [_record_to_solr(record, core_fields, groups.get(record.id, []),
    #                                      fieldvalues.get(record.id, []), media.get(record.id, []))]
    #         conn.add(docs)
    #     return process

    # record_ids = [kwargs['instance'].id]
    # media_dict = _preload_related(Media, record_ids)
    # fieldvalue_dict = _preload_related(FieldValue, record_ids, related=2)
    # groups_dict = _preload_related(CollectionItem, record_ids)

    # process_thread = Thread(target=process_data(groups_dict, fieldvalue_dict, media_dict))
    # process_thread.start()
    # process_thread.join()
    ###


def post_taggeditem_callback(sender, instance, **kwargs):
    if instance and instance.content_type == ContentType.objects.get_for_model(OwnedWrapper):
        instance = instance.object
        if instance and instance.content_type == ContentType.objects.get_for_model(Record):
            mark_for_update(record_id=instance.object_id)


def post_collectionitem_callback(sender, **kwargs):
    mark_for_update(record_id=kwargs['instance'].record.id)


post_delete.connect(post_record_delete_callback, sender=Record)
post_save.connect(post_record_save_callback, sender=Record)

post_delete.connect(post_taggeditem_callback, sender=TaggedItem)
post_save.connect(post_taggeditem_callback, sender=TaggedItem)

post_delete.connect(post_collectionitem_callback, sender=CollectionItem)
post_save.connect(post_collectionitem_callback, sender=CollectionItem)


def disconnect_signals():
    post_delete.disconnect(post_record_delete_callback, sender=Record)
    post_save.disconnect(post_record_save_callback, sender=Record)

    post_delete.disconnect(post_taggeditem_callback, sender=TaggedItem)
    post_save.disconnect(post_taggeditem_callback, sender=TaggedItem)

    post_delete.disconnect(post_collectionitem_callback, sender=CollectionItem)
    post_save.disconnect(post_collectionitem_callback, sender=CollectionItem)
