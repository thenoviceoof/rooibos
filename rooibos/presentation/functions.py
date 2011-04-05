from models import Presentation
from rooibos.util.progressbar import ProgressBar
from django.db import reset_queries


WINDOW_SIZE = 20
THRESHOLD = 0.1

def get_related_items(verbose=False):
    
    total_count = Presentation.objects.count()
    
    if verbose:
        print "Analyzing..."
        pb = ProgressBar(total_count)
        
    count = 0
    
    total_scores = dict()
    
    for presentation in Presentation.objects.all():
        
        def sort_items(item1, item2):
            return (item1, item2) if item1 < item2 else (item2, item1)
        
        items = presentation.items.all().values_list('id', flat=True)
        scores = dict()
        for index1, item1 in zip(range(len(items)), items):
            to_index2 = min(index1 + WINDOW_SIZE, len(items))
            for index2, item2 in zip(range(index1 + 1, to_index2), items[index1 + 1:to_index2]):
                if item1 != item2:
                    key = sort_items(item1, item2)
                    scores[key] = scores.setdefault(key, 0.0) + (1.0 / float(index2 - index1))
        
        for key, score in scores.iteritems():
            total_scores[key] = total_scores.setdefault(key, 0.0) + score
        
        count += 1
        if verbose: pb.update(count)
    
        reset_queries()
    
    if verbose:
        pb.done()
        
        print "Processing..."
        pb = ProgressBar(len(total_scores))
        
    count = 0

    records = dict()
    dropped = 0
    while total_scores:
        (item1, item2), score = total_scores.popitem()
        if score >= THRESHOLD:
            records.setdefault(item1, []).append((item2, score))
            records.setdefault(item2, []).append((item1, score))
        else:
            dropped += 1
        count += 1
        if verbose:
            pb.update(count)
    
    if verbose:
        pb.done()
        print "Dropped %d" % dropped
        
        print "Sorting..."
    
    for key in records.iterkeys():
        records[key].sort(lambda (i1,s1), (i2,s2): 0 if s1==s2 else (-1 if s1>s2 else 1))
        records[key] = map(lambda (item, score): item, records[key])
        
    return records
