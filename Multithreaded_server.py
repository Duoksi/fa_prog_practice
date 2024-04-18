import os
import json
import socket
import struct
import threading
import psutil
import xml.etree.ElementTree as ET
import time

class Node:

    def __init__(self, value):
        self.value = value
        self.left = self.right = None

class Tree:

    def __init__(self):
        self.root = None

    def insert_node(self, node, value):
        if node is None:
            return Node(value)

        if value < node.value:
            node.left = self.insert_node(node.left, value)
        else:
            node.right = self.insert_node(node.right, value)
        return node

    def save_tree_json(self, filename):
        def serialize(node):
            if node is None:
                return None
            return {
                'value': node.value,
                'left': serialize(node.left),
                'right': serialize(node.right)
            }

        serialized_tree = serialize(self.root)
        with open(filename, 'w') as file:
            json.dump(serialized_tree, file, indent=4)

    def save_tree_xml(self, filename):
        def serialize(node, parent):
            if node is None:
                return
            element = ET.SubElement(parent, 'node')
            ET.SubElement(element, 'value').text = str(node.value)
            serialize(node.left, element)
            serialize(node.right, element)

        root_element = ET.Element('root')
        serialize(self.root, root_element)
        tree = ET.ElementTree(root_element)
        tree.write(filename)

def create_directory():
    current_time = time.strftime("%d-%m-%Y_%H-%M-%S")
    directory_name = os.path.join(os.getcwd(), current_time)
    os.makedirs(directory_name)
    return directory_name

def read_json_file(filename):
    with open(filename, 'r') as file:
        data = json.load(file)
    return data
