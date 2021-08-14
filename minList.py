class minList:
    def __init__(self):
        self.toDo_list = []
        self.mindist_list: [int] = []
        self.skyline: ['Node'] = []

    # INSERTS A NODE OR AN ENTRY ALONG WITH ITS MINDIST AND SORTS BOTH LISTS WITH KEY=MINDIST
    def insert(self, node: 'Node' = None, entry: 'Entry' = None, point: 'Point' = None):
        if node is not None:
            self.toDo_list.extend([node])
        else:
            self.toDo_list.extend([entry])
        if point is None:
            self.mindist_list.extend([node.mbr.mindist()])
        else:
            self.mindist_list.extend([node.mbr.mindist(point)])
        list1 = self.toDo_list
        list2 = self.mindist_list
        self.toDo_list, self.mindist_list = (list(s) for s in zip(
            *sorted(zip(list1, list2), key=lambda pair: pair[1])))

    # CHECKS TO SEE IF THE MINLIST OBJECT IS EMPTY
    def isEmpty(self):
        if len(self.mindist_list) != 0:
            return False
        else:
            return True

    # OPENS UP THE FIRST NODE UNTIL WE REACH AN ENTRY. AN ENTRY IS THEN COMPARED WITH THE REST OF THE SKYLINE ENTRIES.
    # IF THE ENTRY IS DOMINATED BY NO OTHER ENTRY INSIDE THE SKYLINE LIST, IT IS ADDED ASWELL.
    def process(self, rec: 'Rectangle' = None):
        isDominatedFlag = 0
        if(len(self.toDo_list) != 0):
            tmp_node = self.toDo_list[0]
            del self.toDo_list[0]
            del self.mindist_list[0]
            if(str(type(tmp_node)) == "<class 'rtree.RTree.Node'>"):
                if len(tmp_node.children) != 0:
                    for num_skylines in range(len(self.skyline)):
                        if tmp_node.mbr.is_dominated(self.skyline[num_skylines].mbr):
                            isDominatedFlag = 1
                    if isDominatedFlag == 0:
                        for num_children in range(len(tmp_node.children)):
                            self.insert(tmp_node.children[num_children])
                elif len(tmp_node.entries) != 0:
                    for num_skylines in range(len(self.skyline)):
                        if tmp_node.mbr.is_dominated(self.skyline[num_skylines].mbr):
                            isDominatedFlag = 1
                    if isDominatedFlag == 0:
                        for num_entries in range(len(tmp_node.entries)):
                            self.insert(tmp_node.entries[num_entries])
            else:
                if len(self.skyline) != 0:
                    for num_skylines in range(len(self.skyline)):
                        if tmp_node.mbr.is_dominated(self.skyline[num_skylines].mbr):
                            isDominatedFlag = 1
                    if isDominatedFlag == 0:
                        if rec is None:
                            self.skyline.extend([tmp_node])
                        else:
                            if rec.contains(tmp_node.mbr):
                                self.skyline.extend([tmp_node])
                else:
                    if rec is None:
                        self.skyline.extend([tmp_node])
                    else:
                        if rec.contains(tmp_node.mbr):
                            self.skyline.extend([tmp_node])

        return self.skyline

    def __repr__(self):
        ret = ""
        for num_nodes in range(len(self.toDo_list)):
            ret += "\nMindist: " + \
                str(self.mindist_list[num_nodes]) + "\n" + \
                self.toDo_list[num_nodes].mbr.__repr__() + "\n"
        return ret
