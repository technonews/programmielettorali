#encoding:UTF-8
from django.core.management import setup_environ
import settings
setup_environ(settings)

import sys

from datetime import datetime, timedelta
from collections import Counter
from backend.models import Adjective, Diary, Sentence, VerbNounPair, Item

from utils import select_data, save_table

def calculate_frequency(sentences, all_features, feature_name):
    freq = {}
    total = all_features.count()
    for cnt, feature in enumerate(all_features):
        dq = {feature_name+'__id__contains': feature.id}
        c = sentences.filter(**dq).count()
        
        k = (feature, 'general')
        
        freq[k] = c
        
        #print feature,',', c
        print "%4d of %4d\r" % (cnt, total),
        if cnt % 20 == 0:
            sys.stdout.flush()
    
    return freq


def calculate_frequency_user(sentences, all_features1, feature1_name):
    freq = {}
    
    total1 = all_features1.count()
    for cnt1, feature1 in enumerate(all_features1):
        #print feature1
        qd1 = {feature1_name+'__id__contains': feature1.id} 
        pre_selected = sentences.filter(**qd1).distinct()

        all_users = [s.diary.user for s in pre_selected]
        all_users = list(set(all_users))
        
        total2 = len(all_users)
        for cnt2, user in enumerate(all_users):
            selected = pre_selected.filter(diary__user=user).distinct()
            c = selected.count()
            
            k = (feature1, user)
            
            freq[k] = c
            #print k, c, pre_selected.count()
            print "%4d of %4d, %4d of %4d\r" % (cnt1, total1, cnt2, total2),
            if cnt2 % 20 == 0:
                sys.stdout.flush()

    return freq

def calculate_dual_frequency(sentences, all_features1, feature1_name, all_features2, feature2_name, diary):
    freq = {}
    
    total1 = all_features1.count()
    for cnt1, feature1 in enumerate(all_features1):
        
        qd1 = {feature1_name+'__id__contains': feature1.id} 
        pre_selected = sentences.filter(**qd1).distinct()
        
        if diary:
            # expand the selection of sentences to all other sentences of 
            # the diary entries they belong to
            diaries = list(set([s.diary for s in pre_selected]))
            pre_selected = sentences.filter(diary__in=diaries)
        
        # restrict all_features2 to the ones contained in the pre_selected sentences
        features2 = all_features2.filter(sentence__id__in=pre_selected)
        #features2 = all_features2 
        
        total2 = features2.count()
        #total2 = len(features2)
        for cnt2, feature2 in enumerate(features2):
            qd2 = {feature2_name + '__id__contains': feature2.id}
            selected = pre_selected.filter(**qd2).distinct()
            if diary:
                c = len(set([x.diary for x in selected]))
            else:
                c = selected.count()
            
            k = (feature1, feature2)
            
            freq[k] = c
            print "%4d of %4d, %4d of %4d\r" % (cnt1, total1, cnt2, total2),
            if cnt2 % 20 == 0:
                sys.stdout.flush()
            #print k, c, pre_selected.count()
            #print "\b" + str(feature1) + ' ' + str(feature2) + "\r",
    return freq

def link_users(links, sentences):
    users = [s.diary.user for s in sentences]
    users = list(set(users))
    for u1 in users:
        for u2 in users:
            # vote for u -- other_u
            #links[(uLUT[u1.id],uLUT[u2.id])] += 1
            try:
                links[(u1,u2)] += 1
            except KeyError:
                links[(u1,u2)] = 1
    

# generic
def count_user_links(selected_sentences, selected_features, feature_name):
    links = {}
    
    total = selected_features.count()
    for cnt, feature in enumerate(selected_features):
        qd = {feature_name + '__id__contains': feature.pk}
        sentences = selected_sentences.filter(**qd)
        link_users(links, sentences)
        
        print "%4d of %4d\r" % (cnt, total),
        if cnt % 20 == 0:
            sys.stdout.flush()
        
    return links


#calculate_frequency(sentences, items, 'referred_items')
def calculate(start, end, name):
    sentences, vnps, adjectives, items = select_data(start, end)
    
    # individual freq
    
    filename = 'items_%d_%s.csv' % (start.year, name)
    print filename
    items_freq = calculate_frequency(sentences, items, 'referred_items')
    save_table(items_freq, open(filename, 'w'))
    
    filename = 'vnps_%d_%s.csv' % (start.year, name)
    print filename
    vnps_freq = calculate_frequency(sentences, vnps, 'verb_noun_pair')
    save_table(vnps_freq, open(filename, 'w'))
    
    filename = 'adjectives_%d_%s.csv' % (start.year, name)
    print filename
    adjs_freq = calculate_frequency(sentences, adjectives, 'adjectives')
    save_table(adjs_freq, open(filename, 'w'))
    

    # user networks
    
    filename = 'vnp_user_net_%d_%s.csv' % (start.year, name)
    print filename
    vnp_links = count_user_links(sentences, vnps, 'verb_noun_pair')
    save_table(vnp_links, open(filename, 'w'))

    filename = 'adj_user_net_%d_%s.csv' % (start.year, name)
    print filename
    adj_links = count_user_links(sentences, adjectives, 'adjectives')
    save_table(adj_links, open(filename, 'w'))

    filename = 'itm_user_net_%d_%s.csv' % (start.year, name)
    print filename
    itm_links = count_user_links(sentences, items, 'referred_items')
    save_table(itm_links, open(filename, 'w'))

    
    # multi-frequencies

    filename = 'item_vs_vnp_%d_%s.csv' % (start.year, name)
    print filename
    item_vs_vnp = calculate_dual_frequency(sentences, items, 'referred_items', vnps, 'verb_noun_pair', diary=True)
    save_table(item_vs_vnp, open(filename, 'w'))
    
    filename = 'item_vs_adj_%d_%s.csv' % (start.year, name)
    print filename
    item_vs_adj = calculate_dual_frequency(sentences, items, 'referred_items', adjectives, 'adjectives', diary=True)
    save_table(item_vs_adj, open(filename, 'w'))
    
    filename = 'vnp_vs_vnp_%d_%s.csv' % (start.year, name)
    print filename
    vnp_vs_vnp = calculate_dual_frequency(sentences, vnps, 'verb_noun_pair', vnps, 'verb_noun_pair', diary=True)
    save_table(vnp_vs_vnp, open(filename, 'w'))
    
    filename = 'adj_vs_adj_%d_%s.csv' % (start.year, name)
    print filename
    adj_vs_adj = calculate_dual_frequency(sentences, adjectives, 'adjectives', adjectives, 'adjectives', diary=True)
    save_table(adj_vs_adj, open(filename, 'w'))
    
    filename = 'user_vs_item_%d_%s.csv' % (start.year, name)
    print filename
    user_vs_item = calculate_frequency_user(sentences, items, 'referred_items')
    save_table(user_vs_item, open(filename, 'w'))
    
    filename = 'user_vs_vnp_%d_%s.csv' % (start.year, name)
    print filename
    user_vs_vnp = calculate_frequency_user(sentences, vnps, 'verb_noun_pair')
    save_table(user_vs_vnp, open(filename, 'w'))
    
    return

if __name__ == '__main__':
    for year in (2011, 2010, 2009, 2008, 2007):
        s_all = datetime(year, 1, 1)
        e_all = datetime(year+1, 1, 1)
        calculate(s_all, e_all, 'all')
        
        year_total = Diary.objects.filter(timestamp__gte=s_all).filter(timestamp__lt=e_all).count()
        s_ini = s_all
        e_ini = s_ini
        while Diary.objects.filter(timestamp__gte=s_all).filter(timestamp__lt=e_all).count() < (year_total / 2):
            e_ini = e_ini + timedelta(days=7)
        calculate(s_ini, e_ini, 'ini')
        
        s_mid = e_ini
        e_mid = e_ini + timedelta(days=10)
        calculate(s_mid, e_mid, 'mid')

