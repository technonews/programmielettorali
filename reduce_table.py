'''
Created on 13 May 2012

@author: enrico
'''

from django.core.management import setup_environ
import settings
from django.contrib.gis.geos.base import numpy
setup_environ(settings)

#from collections import Counter
from utils import load_table_data, get_headers, save_table
from backend.models import Item


# =======
# TODO: test the following!
from hcluster import pdist, linkage, to_tree
from numpy import array

def dict_to_numpy(d):
    rows, cols = get_headers(table)
    res = []
    for r in rows:
        res.append([])
        for c in cols:
            try:
                k = (r, c)
                val = d[k]
            except KeyError:
                val = 0
            res[-1].append(val)
    return array(res)

def collect_leaves(n):
    if n.is_leaf():
        return [n.id,]
    else:
        l = n.get_left()
        r = n.get_right()
        left_leaves = collect_leaves(l)
        right_leaves = collect_leaves(r)
        return left_leaves + right_leaves

def collect_clusters(n, threshold):
    #print 'dist:', n.dist
    #print 'is_leaf:', n.is_leaf()
    if n.dist < threshold or n.is_leaf():
        ids = collect_leaves(n)
        ids.sort()
        #print 'cluster:', ids
        return [ids]
    else:
        l = n.get_left()
        r = n.get_right()
        l_cluster = collect_clusters(l, threshold)
        r_cluster = collect_clusters(r, threshold)
        result = []
        if issubclass(l_cluster[0].__class__, [].__class__):
            result += l_cluster
        else:
            result.append(l_cluster)
        if issubclass(r_cluster[0].__class__, [].__class__):
            result += r_cluster
        else:
            result.append(r_cluster)
        return result

def get_clusters(desired_no_clusters, root):
    for t in range(20):
        t = 1 - t / 20.0
        clusters = collect_clusters(root, t)
        
        #print 't: %.2f, clusters: %d' % (t, len(clusters))
        #print clusters
        #print
        
        if len(clusters) >= desired_no_clusters:
            return clusters
    return clusters


def cluster(x, headers):
    y = pdist(x)
    z = linkage(y)
    
    print z
    root = to_tree(z)
    
    all_leaves = collect_leaves(root)
    all_leaves.sort()
    print 'all leaves:', all_leaves
    
    clusters = get_clusters(6)
    print len(clusters), 'clusters'
    print clusters
    
    lut = {}
    for cl in clusters:
        cluster_name = ",".join([headers[i] for i in cl])
        print cluster_name
        for i in cl:
            lut[headers[i]] = cluster_name
    print
    
    return lut
    
    
def cluster_columns(table, columns):
    x = dict_to_numpy(table)
    return cluster(x, columns)

def cluster_rows(table, rows):
    x = dict_to_numpy(table)
    x = numpy.transpose(x)
    return cluster(x, rows)

# =========


def build_db_items_lut(items):
    #fixed = ('building', 'space')
    lut = {}
    for r in items:
        record_type, number = r.split(' ')
        #number = int(number)
        record_type = record_type.lower()
        
        qd = {record_type + '__number': number}
        items = Item.objects.filter(**qd)
        specific = items.select_subclasses()
        
        i = specific[0]
        location = None
        #try:
        #    location = i.building
        #except (Item.DoesNotExist, AttributeError):
        #    pass
        if not location:
            try:
                location = i.area
            except (Item.DoesNotExist, AttributeError):
                pass
        
        #area_lut[r] = area
        #type_lut[r] = record_type
        
        try:
            f_type = i.feature_type
            record_type = f_type.name + ' (feature)'
        except AttributeError:
            pass
        
        try:
            cat = i.category
            record_type = cat.name + ' (unit)'
        except AttributeError:
            pass
        
        #if record_type in fixed:
        #    record_type = r
        #    location = i.area
        
        lut[r] = (record_type, location)
    
    return lut

def fix_grouped_key(k):
    if k[1] is None:
        return str(k[0]) 
    else:    
        return str(k[0]) + ' in ' + str(k[1]) + ' ' + str(k[1].__class__.__name__)
     

def group_db_items(rows, cols, table):
    try:
        # try to group the rows
        rows_lut = build_db_items_lut(rows)
    except ValueError:x
        # if it does not work
        # we build an "identity" lut
        rows_lut = dict(zip(rows, rows))
    
    try:
        # try to group the columns
        cols_lut = build_db_items_lut(cols)
    except ValueError:
        # if it does not work
        # we build an "identity" lut
        cols_lut = dict(zip(cols, cols))
    print cols_lut
    
    #print Counter(cols_lut.values())
    #print Counter(rows_lut.values())
    
    grouped = {}
    # group data by lut..
    for (r, c) in table.keys():
        r_g = rows_lut[r]
        if r != r_g:
            r_g = fix_grouped_key(r_g)

        c_g = cols_lut[c]
        if c != c_g:
            c_g = fix_grouped_key(c_g)
        #print c, '->', c_g
        
        new_k = (r_g, c_g)
        #print (r, c), '->', new_k
        #print
        
        try:
            grouped[new_k] += table[(r,c)]
        except KeyError:
            grouped[new_k] = table[(r,c)]
    
    return grouped


if __name__ == '__main__':
    import sys
    filename = sys.argv[1]
    
    table = load_table_data(filename)
    rows, cols = get_headers(table)
    
    print cols
    grouped = group_db_items(rows, cols, table)
    
    outfilename = filename.replace('.csv', '_grouped.csv')
    save_table(grouped, open(outfilename, 'w'))
