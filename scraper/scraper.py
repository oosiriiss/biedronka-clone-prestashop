import json
import os
from typing import List, Optional, Dict
import aiohttp
import asyncio
import hashlib
import requests
import re
from bs4 import BeautifulSoup
import logging


"""
    Buduje PageTree
    Tree ma wskaznik HEAD aby od tego miejsca rozpoczac znowu scrapowanie
    Tree zawiera takze linki produktow (produkty to liscie)

    Scraper buduje drzewo
    zapisuje na dysk
    asynchronicznie przetwarza produkty


"""

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class TreeNode:
    def __init__(self, name, url, absolute_path=None):
        self.name = name
        self.url = url
        self.children = []
        self.absolute_path = absolute_path or name

    def add_child(self, node):
        node.absolute_path = self.absolute_path + "/" + node.name
        self.children.append(node)

    def get_children(self):
        return self.children

    def is_leaf(self):
        return not self.children
    
    def to_dict(self):
        return {
            "name": self.name,
            "url": self.url,
            "absolute_path": self.absolute_path,
            "children": [ch.to_dict() for ch in self.children]
        }

    @staticmethod
    def from_dict(data):
        node = TreeNode(data["name"], data["url"], data.get("absolute_path"))
        node.children = [TreeNode.from_dict(ch) for ch in data.get("children", [])]
        return node

    

class PageTree:
    def __init__(self):
        self.root = TreeNode("", "")


    def add_page(self, absolute_path, page_name, page_url):
        parts = absolute_path.split("/") if absolute_path else []
        current_node = self.root

        for part in parts:
            child = next((ch for ch in current_node.get_children() if ch.name == part), None)

            if not child:
                logging.error(f"This branch does not exist {absolute_path}!")
                raise ValueError(f"Branch does not exist: {absolute_path}")

            current_node = child

        child_node = TreeNode(page_name, page_url)
        current_node.add_child(child_node)

        return child_node


    def dfs_leaves_after(self, func, last_processed_path=None):
        skip_node = None
        if last_processed_path:
            skip_node = self.root
            for part in last_processed_path.split("/"):
                skip_node = next((ch for ch in skip_node.get_children() if ch.name == part), None)
                if not skip_node:
                    raise ValueError(f"Last processed path not found: {last_processed_path}")

        found_skip = [skip_node is None]

        def _dfs(node):
            if node.is_leaf():
                if found_skip[0]:
                    func(node)
                elif node == skip_node:
                    found_skip[0] = True

            for ch in node.get_children():
                _dfs(ch)

        _dfs(self.root)


    def save(self, filepath):
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.root.to_dict(), f, ensure_ascii=False, indent=2)

    
    @staticmethod
    def load(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        tree = PageTree()
        tree.root = TreeNode.from_dict(data)
        return tree
    

