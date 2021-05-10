#!/usr/bin/env python3
# coding: utf-8
import beancount.loader
import beancount.core
from tree import Node

def generate_account_hierarchy(account_file: str):
    (entries, _, _) = beancount.loader.load_file(account_file)
    accounts = [e.account for e in entries if type(e) == beancount.core.data.Open and e.meta['filename'] != "<unrealized_gains>"]
    root_node = Node('root')
    for account in accounts:
        segments = account.split(':')
        node = root_node
        for cur_seg in segments:
            if not node.has_child(cur_seg):
                node.add_child(cur_seg)
            node = node.get_child(cur_seg)

    return root_node
