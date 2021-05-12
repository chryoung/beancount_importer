import beancount.core
import beancount.loader
import os

from tree import Node


def generate_account_hierarchy(beancount_file: str) -> Node:
    (entries, _, _) = beancount.loader.load_file(beancount_file)
    accounts = [e.account for e in entries if
                type(e) == beancount.core.data.Open and e.meta['filename'] != '<unrealized_gains>']
    root_node = Node('root')
    for account in accounts:
        segments = account.split(':')
        node = root_node
        for cur_seg in segments:
            if not node.has_child(cur_seg):
                node.add_child(cur_seg)
            node = node.get_child(cur_seg)

    return root_node


def get_operating_currencies(beancount_file: str) -> list:
    if not os.path.isfile(beancount_file):
        return []

    (_, _, options) = beancount.loader.load_file(beancount_file)

    return options['operating_currency']
