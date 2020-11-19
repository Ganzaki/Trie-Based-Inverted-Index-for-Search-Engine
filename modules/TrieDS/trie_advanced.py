"""
    Trie Data Structur is defined here
"""
from copy import deepcopy


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
    """
        set diff algo for list
    """
    s1 = set(li1)
    s2 = set(li2)
    li_dif = []
    for i in s1:
        if i not in s2:
            li_dif.append(i)
    return li_dif


def _dict_merge(a, b):
    """
        merge two dict by merging item of each key
    """
    d = deepcopy(a)
    for i in b.keys():
        if i in d.keys():
            for j in b[i]:
                if j not in d[i]:
                    d[i].append(deepcopy(j))
        else:
            d[i] = deepcopy(b[i])
    return d


class Trie:
    """
        Trie data structure for Inverted Index

        Structure(Ex):
            'abs', 'abc', 'bbc'
            Trie('abs', 'abc', 'bbc') -> {'a':[Trie('bs', 'bc'),[0,1]],
                                            'b': [Trie('bc'), [2]]]}

            Trie('bs', 'bc') - > {'b': [Trie('s', 'c'), [0,1]]}
            Trie('bc') -> {'b': [Trie('c'), [2]]}
            Trie('s', 'c') -> {'s': [Trie(), [0]],
                                'c' : [Trie(), [1]]}
            Trie('c') -> {'c': [Trie(), [2]]}

        Usage(Ex):
            trie = Trie()
            tokens = ['abs', 'abc', 'bbc']
            for i_token in range(len(tokens)):
                trie.add_string(token, i_token)     #i_token is taken as doc_id

            # For search :
            pos = trie.search('abs')
    """

    def __init__(self):
        """
            Constructor to initialize root data-node
        """
        self.__data_node = dict()

    @staticmethod
    def __is_valid_dn(dn):
        """
           Check validity of data-node
        """
        if not isinstance(dn, dict):
            return False

        for i in dn.keys():
            if not isinstance(i, str):
                return False
            if not isinstance(dn[i][0], Trie):
                return False
        return True

    @property
    def data_node(self):
        """
            Getter for data_node
        """
        return self.__data_node.copy()

    @data_node.setter
    def data_node(self, d_n):
        """
            Setter for data_node
        """
        if self.__is_valid_dn(d_n):
            self.__data_node = d_n
        else:
            raise InvalidDataNodeStructure(d_n)

    def add_string(self, string, doc):
        """
            Add index to the data structure with pos and doc_id is hashed as doc
        """

        if len(string) < 1:
            raise IrregularStringLength(string=string)
        _first_char = string[0]
        if _first_char in self.__data_node.keys():
            self.__data_node[_first_char][1].append(doc)
            if len(string) > 1:
                self.__data_node[_first_char][0].add_string(string[1:], doc)
        else:
            self.__data_node[_first_char] = [Trie(), [doc]]
            if len(string) > 1:
                self.__data_node[_first_char][0].add_string(string[1:], doc)

    def search(self, string):
        """
            searching self(Trie) to check presence of 'string'

            input can be wild-card such as string='un*ed'
                normal string such as string = "united"
        """
        if len(string) < 1:
            raise IrregularStringLength(string)

        _first_char = string[0]
        if len(string) == 1:
            if _first_char in self.__data_node.keys():
                pos = self.__data_node[_first_char][1]
                res = []
                tmp = self.__data_node[_first_char][0].data_node
                tmp2 = set()
                for i in tmp.keys():
                    tmp2.update(set(tmp[i][1]))
                for i in pos:
                    if i not in tmp2:
                        res.append(i)
                return res
            if _first_char == '?':
                res = []
                for i in self.__data_node.keys():
                    res = list(set(res+self.search(i)))
                return deepcopy(res)
            if _first_char == '*':
                res = []
                for i in self.__data_node.keys():
                    res = list(set(res+self.__data_node[i][1]))
                return deepcopy(res)
        elif len(string) == 2 and string[-1] == "*":
            if _first_char in self.__data_node.keys():
                return deepcopy(self.__data_node[_first_char][1])
        else:
            if _first_char == '?':
                res = []
                for i in self.__data_node.keys():
                    res = list(set(res+self.__data_node[i][0].search(string[1:])))
                return deepcopy(res)
            if _first_char == '*':
                res = self.search(string[1:])
                for i in self.__data_node.keys():
                    res = list(set(res+self.__data_node[i][0].search(string)))
                return deepcopy(res)
            if _first_char in self.__data_node.keys():
                return self.__data_node[_first_char][0].search(string[1:])
        return []

    def merge(self, trie):
        """
            class method to merge two tries
        """
        _dn = trie.data_node
        for i in _dn.keys():
            if i in self.__data_node.keys():
                self.__data_node[i][1] = list(
                    set(self.__data_node[i][1] + _dn[i][1]))
                self.__data_node[i][0].merge(_dn[i][0])
            else:
                self.__data_node[i] = deepcopy(_dn[i])

    def to_dict(self):
        """
            Convert Trie to completely dict form and return the dict
        """
        if not self.__data_node:
            return {}
        req_dict = {}
        for i in self.__data_node.keys():
            req_dict[i] = [self.__data_node[i]
                           [0].to_dict(), deepcopy(self.__data_node[i][1])]
        return req_dict

    def from_dict(self, trie_dict):
        """
            Load Trie from the dict
        """
        if not trie_dict:
            self.__data_node = {}
            return

        for i in trie_dict.keys():
            new_trie = Trie()
            new_trie.from_dict(trie_dict[i][0])
            self.__data_node[i] = [new_trie, [int(jj) for jj in trie_dict[i][1]]]


def merge(a, b):
    """
        Merge two trie
    """
    dn_1 = a.data_node
    dn_2 = b.data_node
    dn_3 = {}

    # copy
    dn_3 = deepcopy(dn_1)

    for i in dn_2.keys():
        if i in dn_3.keys():
            dn_3[i][1] = list(set(dn_3[i][1] + dn_2[i][1]))
            dn_3[i][0] = merge(dn_3[i][0], dn_2[i][0])
        else:
            dn_3[i] = deepcopy(dn_2[i])
    c = Trie()
    c.data_node = dn_3
    return c
