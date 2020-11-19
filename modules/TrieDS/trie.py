import copy


class IrregularStringLength(Exception):
    """
        Raised when string length is different from expected
    """

    def __init__(self, string, message="String length is 0"):
        self.string = string
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'{self.string} -> {self.message}'


class InvalidDataNodeStructure(Exception):
    """
        Raised when string length is different from expected
    """

    def __init__(self, dn, message="Invalid Structure try something else or use your brain"):
        self.dn = dn
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'{self.dn} -> {self.message}'


def _list_diff(li1, li2):
    s1 = set(li1)
    s2 = set(li2)
    li_dif = []
    for i in s1:
        if i not in s2:
            li_dif.append(i)
    return li_dif


def _dict_merge(a, b):
    """
    """
    d = copy.deepcopy(a)
    for i in b.keys():
        if i in d.keys():
            for j in b[i]:
                if j not in d[i]:
                    d[i].append(copy.deepcopy(j))
        else:
            d[i] = copy.deepcopy(b[i])
    return d


class Trie:
    """
    docstring
    """

    def __init__(self):
        self.__data_node = dict()

    @staticmethod
    def __is_valid_dn(dn):
        if type(dn) != dict:
            return False

        for i in dn.keys():
            if type(i) != str:
                return False
            if type(dn[i][0]) != Trie:
                return False
        return True

    @property
    def data_node(self):
        return self.__data_node.copy()

    @data_node.setter
    def data_node(self, dn):
        if self.__is_valid_dn(dn):
            self.__data_node = dn
        else:
            raise InvalidDataNodeStructure(dn)

    ## V1 ##

    def add_string_with_pos(self, first_char, string, doc_id, row, pos):
        """
            Add index to the data structure
        """
        if len(first_char) != 1:
            raise IrregularStringLength(
                string=first_char, message="first_char length is not 1")

        if first_char in self.__data_node.keys():
            if len(string) == 0 or first_char == "*":
                if doc_id in self.__data_node[first_char][1].keys():
                    self.__data_node[first_char][1][doc_id].append([row, pos])
                else:
                    self.__data_node[first_char][1][doc_id] = [[row, pos]]
            if len(string) > 0:
                self.__data_node[first_char][0].add_string(
                    string[0], string[1:], doc_id, row, pos)
            elif first_char != "*":
                self.__data_node[first_char][0].add_string(
                    "*", "", doc_id, row, pos)
        else:
            self.__data_node[first_char] = [Trie(), {doc_id: [[row, pos]]}]
            if len(string) > 0:
                self.__data_node[first_char][0].add_string(
                    string[0], string[1:], doc_id, row, pos)
            elif first_char != "*":
                self.__data_node[first_char][0].add_string(
                    "*", "", doc_id, row, pos)

        if first_char != "*":
            if '*' in self.__data_node.keys():
                if doc_id in self.__data_node['*'][1].keys():
                    self.__data_node['*'][1][doc_id].append([row, pos])
                else:
                    self.__data_node['*'][1][doc_id] = [[row, pos]]
                if len(string) > 0:
                    self.__data_node['*'][0].add_string(
                        string[0], string[1:], doc_id, row, pos)

            else:
                self.__data_node['*'] = [Trie(), {doc_id: [[row, pos]]}]
                if len(string) > 0:
                    self.__data_node['*'][0].add_string(
                        string[0], string[1:], doc_id, row, pos)

    #########

    #### V2 ####

    def add_string_with_docnrow(self, first_char, string, doc_id, row):
        """
            Add index to the data structure
        """
        if len(first_char) != 1:
            raise IrregularStringLength(
                string=first_char, message="first_char length is not 1")

        if first_char in self.__data_node.keys():
            if len(string) == 0 or first_char == "*":
                if doc_id in self.__data_node[first_char][1].keys():
                    self.__data_node[first_char][1][doc_id].append(row)
                else:
                    self.__data_node[first_char][1][doc_id] = [row]
            if len(string) > 0:
                self.__data_node[first_char][0].add_string(
                    string[0], string[1:], doc_id, row)
            elif first_char != "*":
                self.__data_node[first_char][0].add_string(
                    "*", "", doc_id, row)
        else:
            self.__data_node[first_char] = [Trie(), {doc_id: [row]}]
            if len(string) > 0:
                self.__data_node[first_char][0].add_string(
                    string[0], string[1:], doc_id, row)
            elif first_char != "*":
                self.__data_node[first_char][0].add_string(
                    "*", "", doc_id, row)

        if first_char != "*":
            if '*' in self.__data_node.keys():
                if doc_id in self.__data_node['*'][1].keys():
                    self.__data_node['*'][1][doc_id].append(row)
                else:
                    self.__data_node['*'][1][doc_id] = [row]
                if len(string) > 0:
                    self.__data_node['*'][0].add_string(
                        string[0], string[1:], doc_id, row)

            else:
                self.__data_node['*'] = [Trie(), {doc_id: [row]}]
                if len(string) > 0:
                    self.__data_node['*'][0].add_string(
                        string[0], string[1:], doc_id, row)
    ########

    ### V3 ###

    def add_string(self, first_char, string, doc):
        """
            Add index to the data structure
        """
        if len(first_char) != 1:
            raise IrregularStringLength(
                string=first_char, message="first_char length is not 1")

        if first_char in self.__data_node.keys():
            if len(string) == 0 or first_char == "*":
                self.__data_node[first_char][1].append(doc)
            if len(string) > 0:
                self.__data_node[first_char][0].add_string(
                    string[0], string[1:], doc)
            elif first_char != "*":
                self.__data_node[first_char][0].add_string("*", "", doc)
        else:
            self.__data_node[first_char] = [Trie(), [doc]]
            if len(string) > 0:
                self.__data_node[first_char][0].add_string(
                    string[0], string[1:], doc)
            elif first_char != "*":
                self.__data_node[first_char][0].add_string("*", "", doc)

        if first_char != "*":
            if '*' in self.__data_node.keys():
                self.__data_node['*'][1].append(doc)
                if len(string) > 0:
                    self.__data_node['*'][0].add_string(
                        string[0], string[1:], doc)
            else:
                self.__data_node['*'] = [Trie(), [doc]]
                if len(string) > 0:
                    self.__data_node['*'][0].add_string(
                        string[0], string[1:], doc)

    ##########

    #### V1 ####

    def search_docrow(self, string):
        """
        """
        if len(string) < 1:
            raise IrregularStringLength(string)

        _first_char = string[0]
        if len(string) == 1:
            if _first_char in self.__data_node.keys():
                if _first_char != '*':
                    pos = copy.deepcopy(self.__data_node[_first_char][1])
                    extra = {}
                    if '*' in self.__data_node['*'][0].__data_node.keys():
                        extra = self.__data_node['*'][0].__data_node['*'][1]
                    for i in extra.keys():
                        if i in pos.keys():
                            pos[i] = _list_diff(pos[i], extra[i])
                            if not pos[i]:
                                pos.pop(i)
                    return pos
                return copy.deepcopy(self.__data_node[_first_char][1])
        else:
            if _first_char in self.__data_node.keys():
                if _first_char == '*':
                    pos_star = self.__data_node[_first_char][0].search_docrow(
                        string)
                    pos_char1 = self.search_docrow(string[1:])
                    pos_char2 = self.__data_node[_first_char][0].search_docrow(
                        string[1:])
                    return _dict_merge(pos_star, _dict_merge(pos_char1, pos_char2))
                return self.__data_node[_first_char][0].search_docrow(string[1:])

        return {}
    ##########

    def search(self, string):
        """
        """
        if len(string) < 1:
            raise IrregularStringLength(string)

        _first_char = string[0]
        if len(string) == 1:
            if _first_char in self.__data_node.keys():
                if _first_char != '*':
                    pos = copy.deepcopy(self.__data_node[_first_char][1])
                    extra = []
                    if '*' in self.__data_node['*'][0].__data_node.keys():
                        extra = self.__data_node['*'][0].__data_node['*'][1]
                    for i in extra:
                        if i in pos:
                            pos.remove(i)
                    return pos
                return copy.deepcopy(self.__data_node[_first_char][1])
        else:
            if _first_char in self.__data_node.keys():
                if _first_char == '*':
                    pos_star = self.__data_node[_first_char][0].search(string)
                    pos_char1 = self.search(string[1:])
                    pos_char2 = self.__data_node[_first_char][0].search(
                        string[1:])
                    return list(set(pos_star + pos_char1 + pos_char2))
                return self.__data_node[_first_char][0].search(string[1:])
        return []

    def merge_docrow(self, trie):
        """
        """
        assert(type(trie) == Trie)
        dn = trie.data_node
        for i in dn.keys():
            if i in self.__data_node.keys():
                self.__data_node[i][1] = _dict_merge(
                    self.__data_node[i][1], dn[i][1])
                self.__data_node[i][0].merge(dn[i][0])
            else:
                self.__data_node[i] = copy.deepcopy(dn[i])

    def merge(self, trie):
        """
        """
        assert(type(trie) == Trie)
        dn = trie.data_node
        for i in dn.keys():
            if i in self.__data_node.keys():
                self.__data_node[i][1] = list(
                    set(self.__data_node[i][1] + dn[i][1]))
                self.__data_node[i][0].merge(dn[i][0])
            else:
                self.__data_node[i] = copy.deepcopy(dn[i])

    def to_dict(self):
        """
        """
        if not self.__data_node:
            return {}
        req_dict = {}
        for i in self.__data_node.keys():
            req_dict[i] = [self.__data_node[i]
                           [0].to_dict(), copy.deepcopy(self.__data_node[i][1])]
        return req_dict

    

def merge_docrow(a, b):
    """
        Merge two trie
    """
    assert(type(a) == Trie and type(b) == Trie)
    dn_1 = a.data_node
    dn_2 = b.data_node
    dn_3 = {}

    # copy
    dn_3 = copy.deepcopy(dn_1)

    for i in dn_2.keys():
        if i in dn_3.keys():
            dn_3[i][1] = _dict_merge(dn_3[i][1], dn_2[i][1])
            dn_3[i][0] = merge(dn_3[i][0], dn_2[i][0])
        else:
            dn_3[i] = copy.deepcopy(dn_2[i])
    c = Trie()
    c.data_node = dn_3
    return c


def merge(a, b):
    """
        Merge two trie
    """
    assert(type(a) == Trie and type(b) == Trie)
    dn_1 = a.data_node
    dn_2 = b.data_node
    dn_3 = {}

    # copy
    dn_3 = copy.deepcopy(dn_1)

    for i in dn_2.keys():
        if i in dn_3.keys():
            dn_3[i][1] = list(set(dn_3[i][1] + dn_2[i][1]))
            dn_3[i][0] = merge(dn_3[i][0], dn_2[i][0])
        else:
            dn_3[i] = copy.deepcopy(dn_2[i])
    c = Trie()
    c.data_node = dn_3
    return c
