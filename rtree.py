import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.colorbar as cbar
import matplotlib.cm as cm
import copy
import random
import csv
import os
from rectangle import Rectangle, Point
from entry import Entry, Rectangle, Point
from random import randint
from minList import *
from pandas import read_csv
from time import perf_counter


MAX_ENTRIES = 4
MAX_ROOT_AREA = 1000


class RTree:

    def __init__(self):
        self.root: 'Node' = None
        self.skyline: [Entry] = []

    # MAIN METHOD TO INSERT ENTRIES INTO THE TREE. OF TREE IS EMPTY, IT CREATES ROOT NODE
    def insert(self, entry: Entry):
        if self.root is None:
            self.root = self.Node(mbr=Rectangle(Point(0, 0), Point(100, 100)))
        self.root.insert(entry)

    # CREATES RANDOM POINT ENTRIES
    def create_random_points(self, size_num: int, r_seed: int = None):
        tic = perf_counter()
        random.seed(a=r_seed)
        tmp_entry: Entry = None
        tmp_rect: Rectangle = None
        tmp_entry_list: [Entry] = []
        for i in range(size_num):
            tmp_point_lower_left = Point(randint(4, 98), randint(4, 98))
            tmp_point_upper_right = Point(
                tmp_point_lower_left.x, tmp_point_lower_left.y)
            tmp_rect = Rectangle(tmp_point_lower_left, tmp_point_upper_right)
            tmp_letter = "E"+str(i)
            tmp_entry = Entry(tmp_letter, tmp_rect)
            self.insert(tmp_entry)
            tmp_entry_list.extend([tmp_entry])
        toc = perf_counter()
        time_elapsed_tree = toc - tic
        return tmp_entry_list, time_elapsed_tree

    # CREATES AN RTREE FROM A GIVEN CSV WHICH CONTAINS X AND Y COORDINATES
    def import_csv(self, data_set: str):
        i = 0
        os.chdir(os.path.dirname(__file__))
        df = read_csv('data-sets\\' + data_set + '.csv')
        tmp_entry: Entry = None
        tmp_rect: Rectangle = None
        tmp_entry_list: [Entry] = []
        tic = perf_counter()
        for x, y, _ in zip(df['x'], df['y'], df['z']):
            tmp_point_lower_left = Point(x, y)
            tmp_point_upper_right = Point(x, y)
            tmp_rect = Rectangle(tmp_point_lower_left, tmp_point_upper_right)
            tmp_letter = "E"+str(i)
            i += 1
            tmp_entry = Entry(tmp_letter, tmp_rect)
            self.insert(tmp_entry)
            tmp_entry_list.extend([tmp_entry])
        toc = perf_counter()
        time_elapsed_tree = toc - tic
        return tmp_entry_list, time_elapsed_tree

    # PLOT THE TREE IF THE ENTRIES ARE POINTS
    def show_points(self):
        self.root.show_points()

    # CALCULATES THE TREES SKYLINE USING THE BBS ALGORITHM
    def bbs_skyline(self):
        tic = perf_counter()
        minlist = minList()
        skyline: [Entry] = []
        if len(self.root.children) != 0:
            for num_children in range(len(self.root.children)):
                minlist.insert(self.root.children[num_children])
        else:
            minlist.insert(self.root)

        while not minlist.isEmpty():
            skyline = minlist.process()

        self.skyline = skyline
        toc = perf_counter()
        time_elapsed_skyline = toc - tic
        return skyline, time_elapsed_skyline

    # CALCULATED THE SKYLINE ENTRIES IN THE TREE GIVEN A RANGE QUERY
    def bbs_skyline_range_query(self, rec: 'Rectangle'):
        tic = perf_counter()
        minlist = minList()
        skyline: [Entry] = []
        if len(self.root.children) != 0:
            for num_children in range(len(self.root.children)):
                minlist.insert(
                    self.root.children[num_children], rec.lower_left)
        else:
            minlist.insert(self.root, rec.lower_left)

        while not minlist.isEmpty():
            skyline = minlist.process(rec)

        self.skyline = skyline
        toc = perf_counter()
        time_elapsed_skyline = toc - tic
        return skyline, time_elapsed_skyline

    # RETURNS ENTRIES BASED ON A RECTANGLE THE USER GAVE'
    def range_query(self, rec: Rectangle):
        return self.root.range_query(rec)

    # PLOTS THE TREES SKYLINE
    def show_skyline(self, skyline: [Entry] = None):
        self.root.show_skyline(skyline)

    def __repr__(self):
        ret = repr(self.root)
        return ret

    class Node():
        def __init__(self, mbr: Rectangle = None):
            self.mbr: Rectangle = mbr
            self.children: [__class__] = []
            self.entries: [Entry] = []

        # INSERTS AN ENTRY INTO THE APPROPRIATE NODE. IF SAID NODE EXCEEDS MAX_ENTRIES, IT SPLITS INTO TWO NODES
        # THIS ALSO HANDLES THE SPLIT OF INTERNAL NODES BY ADJUSTING THE TREE
        def insert(self, entry: Entry, level=0):
            if len(self.children) == 0 and level == 0:
                split_node_a, split_node_b = self.insert_entry(entry)
                self.mbr.expand_to_contain(entry.mbr)
                if(split_node_a != None):
                    self.entries.clear()
                    self.children.extend([split_node_a, split_node_b])
                    self.mbr.expand_to_contain(split_node_a.mbr)
                    self.mbr.expand_to_contain(split_node_b.mbr)
                return None, None
            elif len(self.children) == 0 and level != 0:
                split_node_a, split_node_b = self.insert_entry(entry)
                if(split_node_a != None):
                    return split_node_a, split_node_b
                return None, None
            elif len(self.children) != 0 and level == 0:
                if len(self.children[0].children) != 0:
                    index = self.choose_node(entry)
                    split_node_a, split_node_b = self.children[index].insert(
                        entry, level + 1)
                    self.mbr.expand_to_contain(entry.mbr)
                    if(split_node_a != None):
                        del self.children[index]
                        self.children.extend([split_node_a, split_node_b])
                        self.mbr.expand_to_contain(split_node_a.mbr)
                        self.mbr.expand_to_contain(split_node_b.mbr)
                        if len(self.children) > MAX_ENTRIES:
                            split_node_a, split_node_b = self.linear_split_nodes()
                            self.children.clear()
                            self.children.extend([split_node_a, split_node_b])
                            self.mbr.expand_to_contain(split_node_a.mbr)
                            self.mbr.expand_to_contain(split_node_b.mbr)
                    else:
                        self.mbr.expand_to_contain(self.children[index].mbr)
                else:
                    index = self.choose_node(entry)
                    split_node_a, split_node_b = self.children[index].insert_entry(
                        entry)
                    if(split_node_a != None):
                        del self.children[index]
                        self.children.extend([split_node_a, split_node_b])
                        self.mbr.expand_to_contain(split_node_a.mbr)
                        self.mbr.expand_to_contain(split_node_b.mbr)
                        if len(self.children) > MAX_ENTRIES:
                            split_node_a, split_node_b = self.linear_split_nodes()
                            self.children.clear()
                            self.children.extend([split_node_a, split_node_b])
                            self.mbr.expand_to_contain(split_node_a.mbr)
                            self.mbr.expand_to_contain(split_node_b.mbr)
                    else:
                        self.mbr.expand_to_contain(self.children[index].mbr)
                return None, None
            elif len(self.children) != 0 and level != 0:
                if len(self.children[0].children) != 0:
                    index = self.choose_node(entry)
                    split_node_a, split_node_b = self.children[index].insert(
                        entry, level + 1)
                    if(split_node_a != None):
                        del self.children[index]
                        self.children.extend([split_node_a, split_node_b])
                        if len(self.children) > MAX_ENTRIES:
                            split_node_a, split_node_b = self.linear_split_nodes()
                            return split_node_a, split_node_b
                    else:
                        self.mbr.expand_to_contain(self.children[index].mbr)
                else:
                    index = self.choose_node(entry)
                    split_node_a, split_node_b = self.children[index].insert_entry(
                        entry)
                    if(split_node_a != None):
                        del self.children[index]
                        self.children.extend([split_node_a, split_node_b])
                        self.mbr.expand_to_contain(split_node_a.mbr)
                        self.mbr.expand_to_contain(split_node_b.mbr)
                        if len(self.children) > MAX_ENTRIES:
                            split_node_a, split_node_b = self.linear_split_nodes()
                            self.mbr.expand_to_contain(split_node_a.mbr)
                            self.mbr.expand_to_contain(split_node_b.mbr)
                            return split_node_a, split_node_b
                    else:
                        self.mbr.expand_to_contain(self.children[index].mbr)
                return None, None

        # INSERTS AN ENTRY INTO A LEAF NODE. IF IT EXCEEDS MAX_ENTRIES IT SPLITS INTO TWO NODES
        def insert_entry(self, entry: Entry):
            self.entries.append(entry)

            if not self.mbr.contains(entry.mbr):
                self.mbr.expand_to_contain(entry.mbr)

            if len(self.entries) > MAX_ENTRIES:
                split_node_a, split_node_b = self.linear_split_entries()
                return split_node_a, split_node_b

            return None, None

        # SPLITS LEAF NODES INTO TWO WITH THE LINEAR SPLIT ALGORITHM
        def linear_split_entries(self):
            highest_low_index, lowest_high_index = self.choose_seeds_entries()
            leaf_split_1 = self.__class__(mbr=Rectangle.create_mbr_for_entry(
                self.entries[highest_low_index].mbr))
            leaf_split_1.insert_entry(self.entries[highest_low_index])
            leaf_split_2 = self.__class__(mbr=Rectangle.create_mbr_for_entry(
                self.entries[lowest_high_index].mbr))
            leaf_split_2.insert_entry(self.entries[lowest_high_index])
            for num_entries in range(len(self.entries)):
                if num_entries != highest_low_index and num_entries != lowest_high_index:
                    tmp_rect_1 = Rectangle(copy.copy(leaf_split_1.mbr.lower_left), copy.copy(
                        leaf_split_1.mbr.upper_right))
                    tmp_rect_2 = Rectangle(copy.copy(leaf_split_2.mbr.lower_left), copy.copy(
                        leaf_split_2.mbr.upper_right))
                    expansion_cost_1 = tmp_rect_1.expansion_area_cost(
                        self.entries[num_entries].mbr)
                    expansion_cost_2 = tmp_rect_2.expansion_area_cost(
                        self.entries[num_entries].mbr)
                    if expansion_cost_1 <= expansion_cost_2:
                        leaf_split_1.insert(self.entries[num_entries])
                        leaf_split_1.mbr.expand_to_contain(
                            self.entries[num_entries].mbr)
                    else:
                        leaf_split_2.insert(self.entries[num_entries])
                        leaf_split_2.mbr.expand_to_contain(
                            self.entries[num_entries].mbr)

            return leaf_split_1, leaf_split_2

        # SPLITS INTERNAL NODES INTO TWO WITH THE LINEAR SPLIT ALGORITHM
        def linear_split_nodes(self):
            highest_low_index, lowest_high_index = self.choose_seeds_nodes()
            node_split_1 = self.__class__(mbr=Rectangle.create_mbr_for_entry(
                self.children[highest_low_index].mbr))
            node_split_1.children.extend([self.children[highest_low_index]])
            node_split_2 = self.__class__(mbr=Rectangle.create_mbr_for_entry(
                self.children[lowest_high_index].mbr))
            node_split_2.children.extend([self.children[lowest_high_index]])
            for num_children in range(len(self.children)):
                if num_children != highest_low_index and num_children != lowest_high_index:
                    tmp_rect_1 = Rectangle(copy.copy(node_split_1.mbr.lower_left), copy.copy(
                        node_split_1.mbr.upper_right))
                    tmp_rect_2 = Rectangle(copy.copy(node_split_2.mbr.lower_left), copy.copy(
                        node_split_2.mbr.upper_right))
                    expansion_cost_1 = tmp_rect_1.expansion_area_cost(
                        self.children[num_children].mbr)
                    expansion_cost_2 = tmp_rect_2.expansion_area_cost(
                        self.children[num_children].mbr)
                    if expansion_cost_1 <= expansion_cost_2:
                        node_split_1.children.extend(
                            [self.children[num_children]])
                        node_split_1.mbr.expand_to_contain(
                            self.children[num_children].mbr)
                    else:
                        node_split_2.children.extend(
                            [self.children[num_children]])
                        node_split_2.mbr.expand_to_contain(
                            self.children[num_children].mbr)

            return node_split_1, node_split_2

        # THIS METHOD IS USED BY A SPLITTING LEAF NODE TO CHOOSE 2 SEEDS FOR THE SPLIT.
        def choose_seeds_entries(self):
            highest_low_index = 0
            lowest_high_index = 1
            for num_entries in range(len(self.entries)):
                if self.entries[highest_low_index].mbr.lower_left.y < self.entries[num_entries].mbr.lower_left.y:
                    highest_low_index = num_entries

            for num_entries in range(len(self.entries)):
                if self.entries[lowest_high_index].mbr.upper_right.y > self.entries[num_entries].mbr.upper_right.y:
                    if num_entries != highest_low_index:
                        lowest_high_index = num_entries

            return highest_low_index, lowest_high_index

        # THIS METHOD IS USED BY A SPLITTING INTERNAL NODE TO CHOOSE 2 SEEDS FOR THE SPLIT. DIFFERENCE IS IT CHOOSES OTHER NODES AND NOT ENTRIES
        def choose_seeds_nodes(self):
            highest_low_index = 0
            lowest_high_index = 1
            for num_children in range(len(self.children)):
                if self.children[highest_low_index].mbr.lower_left.y < self.children[num_children].mbr.lower_left.y:
                    highest_low_index = num_children

            for num_children in range(len(self.children)):
                if self.children[lowest_high_index].mbr.upper_right.y > self.children[num_children].mbr.upper_right.y:
                    if num_children != highest_low_index:
                        lowest_high_index = num_children

            return highest_low_index, lowest_high_index

        # THIS METHOD RETURNS THE NODE WHICH HAS THE LOWEST EXPANSION COST FOR A GIVEN ENTRY
        def choose_node(self, entry: Entry, leaf_index=0, expansion_cost=MAX_ROOT_AREA):
            for num_entries in range(len(self.children)):
                if self.children[num_entries].mbr.contains(entry.mbr):
                    return num_entries
                else:
                    temp_rect = Rectangle(copy.copy(self.children[num_entries].mbr.lower_left), copy.copy(
                        self.children[num_entries].mbr.upper_right))
                    temp_cost = temp_rect.expansion_area_cost(entry.mbr)
                    if temp_cost < expansion_cost:
                        expansion_cost = temp_cost
                        leaf_index = num_entries

            return leaf_index

        # PLOTS THE TREE FROM THE ROOT NODE IF THE ENTRIES ARE POINTS
        def show_points(self, level=0, ax=None, c=None):
            width, height, _ = self.mbr.calculate_properties()
            np.random.seed(1)
            if level == 0:
                fig = plt.figure()
                ax = fig.add_subplot(111, aspect='equal')
                plt.xlim([self.mbr.lower_left.x - 10,
                          self.mbr.upper_right.x + 10])
                plt.ylim([self.mbr.lower_left.y - 10,
                          self.mbr.upper_right.y + 10])
                colors = np.random.rand(100)
                cmap = cm.get_cmap("hsv")
                c = cmap(colors)

            ax.add_patch(matplotlib.patches.Rectangle(
                (self.mbr.lower_left.x, self.mbr.lower_left.y), width, height, fill=None, edgecolor=c[level+1]))
            if len(self.children) != 0:
                for child in self.children:
                    child.show_points(level + 1, ax, c)
                if level != 0:
                    return
            else:
                for entry in self.entries:
                    circle = plt.Circle(
                        (entry.mbr.lower_left.x, entry.mbr.lower_left.y), 0.5, color='blue')
                    ax.add_patch(circle)
                if level != 0:
                    return
            plt.show()
            return

        # SPLOTS THE TREE FROM THE ROOT NODE IF THE ENTRIES ARE POINTS, CHANGING THE COLOR OF THE SKYLINE
        def show_skyline(self, skylines: [Entry] = None, level=0, ax=None, c=None):
            width, height, _ = self.mbr.calculate_properties()
            np.random.seed(1)
            if level == 0:
                fig = plt.figure()
                ax = fig.add_subplot(111, aspect='equal')
                plt.xlim([self.mbr.lower_left.x - 10,
                          self.mbr.upper_right.x + 10])
                plt.ylim([self.mbr.lower_left.y - 10,
                          self.mbr.upper_right.y + 10])
                colors = np.random.rand(100)
                cmap = cm.get_cmap("hsv")
                c = cmap(colors)

            ax.add_patch(matplotlib.patches.Rectangle(
                (self.mbr.lower_left.x, self.mbr.lower_left.y), width, height, fill=None, edgecolor=c[level+1]))
            if len(self.children) != 0:
                for child in self.children:
                    child.show_skyline(skylines, level + 1, ax, c)
                if level != 0:
                    return
            else:
                for entry in self.entries:
                    circle = plt.Circle(
                        (entry.mbr.lower_left.x, entry.mbr.lower_left.y), 0.5, color='blue')
                    ax.add_patch(circle)
                if level != 0:
                    return

            for skyline in skylines:
                circle = plt.Circle(
                    (skyline.mbr.lower_left.x, skyline.mbr.lower_left.y), 1, color='coral')
                ax.add_patch(circle)
            plt.show()
            return

        # RETURNS ALL THE ENTRIES THAT ARE CONTAINED IN A GIVEN RECTANGLE
        def range_query(self, rec: Rectangle, range_entries: [Entry] = []):
            tic = perf_counter()
            if len(self.children) != 0:
                for num_children in range(len(self.children)):
                    if rec.overlaps(self.children[num_children].mbr):
                        self.children[num_children].range_query(
                            rec, range_entries)
            else:
                for num_entries in range(len(self.entries)):
                    if rec.contains(self.entries[num_entries].mbr):
                        range_entries.extend([self.entries[num_entries]])
            toc = perf_counter()
            time_elapsed_range_query = toc - tic
            return range_entries, time_elapsed_range_query

        def __repr__(self, level=0):
            ret = "\t"*level+self.mbr.__repr__(level)+"\n"
            if len(self.children) != 0:
                for child in self.children:
                    ret += child.__repr__(level+1)
                return ret
            else:
                for entry in self.entries:
                    ret += entry.__repr__(level+1)
                return ret
