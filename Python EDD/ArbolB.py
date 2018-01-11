import bisect
from graphviz import Digraph


class _BTreeNode(object):
    datos = ''

    def __init__(self, values=None, children=None, accesos=None):
        self.parent = None
        self.values = values or []
        self.children = children
        self.accesos = accesos

        # if self.children:
        #     print '------si sale esto es porque no se que hace esto '
        #     for i in self.children:
        #         print '------si sale esto es porque no se que hace esto '
        #         print self.datos
        #         i.parent = self

    def __str__(self):
        return '%r' % self.values

    def pretty_print(self, tab=''):
        print('%s%s' % (tab, self))
        if self.children:
            for i in self.children:
                i.pretty_print(tab + '***')

    contador = 0

    def graficar(self, contador):
        # print 'HOJAS'
        #self.llenar(str("subgraph cluster_" + str(contador) + '{ \n'))

        # self.datos += str("subgraph cluster_" + '{ \n')
        for x in range(0, len(self.values)):
         #   self.llenar(str(self.values[x]) + ' \n')
            print str(self.values[x])
            # self.datos += str(self.values[x]) + ' \n'
        # self.datos += str('} \n')
        #self.llenar(str('} \n'))

        # print self.datos
        if self.children:

            # print '----Nodo padre, hacia las hojas-------'
            # print self.datos
            # print '---fin del recorrdio del nodo padre hacia las hojas------'
            for i in self.children:

         #       self.contador += 1
                i.graficar(self.contador)
                print str(i) + 'no se que es esto parte 2'

    def llenar(self, texto):
        _BTreeNode.datos += texto

    def GenerarArchivo(self):
        print _BTreeNode.datos

    def graficarGrap(self, texto):
        g = Digraph('G', filename='graficaB.gv')
        g.body.append('rankdir=LR')
        g.attr('node', shape='box', color='blue')

        g.body.append(texto)

        g.body.append('label = "Arbol B"')
        g.format = 'png'
        g.view()

    def check_valid(self, tree):
        innerNode = self.children is not None
        rootNode = self.parent is None

        assert (self.values is not None)

        if not rootNode and innerNode:
            assert (tree.min_values <= len(self.values))

        assert (len(self.values) <= tree.max_values)

        if rootNode and innerNode:
            assert (len(self.children) >= 2)

        if innerNode:
            assert ((len(self.values) + 1) == len(self.children))

        prev = None
        for i in self.values:
            if prev is not None:
                assert (i > prev)
            prev = i

        if self.children:
            for i in self.children:
                assert (i.parent is self)
                i.check_valid(tree)

    def search(self, val):
        i = bisect.bisect_left(self.values, val)
        if (i != len(self.values) and not val < self.values[i]):
            assert (self.values[i] == val)
            # return (True,self.values[i], self, i)
            return self.values[i], self, i

        if self.children is not None:
            assert (len(self.children) >= i and self.children[i])
            # buscar recursivamente en el nodo secundario apropiado
            return self.children[i].search(val)
        else:
            # return (False, self, i)
            return False, self, i

    def _split_node(self, tree, val=None, slot=None, childNodes=None):
        assert (val is None or (slot is not None))

        midList = [] if val is None else [val]
        if slot is None:
            slot = 0

        splitValues = self.values[0:slot] + midList + self.values[slot:]
        medianIdx = len(splitValues) // 2

        lv = splitValues[0:medianIdx]
        medianVal = splitValues[medianIdx]
        rv = splitValues[medianIdx + 1:]

        innerNode = self.children is not None

        if innerNode:
            if childNodes is not None:
                splitChildren = (self.children[0:slot] + list(childNodes) + self.children[slot + 1:])
            else:
                splitChildren = self.children
            lc = splitChildren[0:len(lv) + 1]
            rc = splitChildren[len(lv) + 1:]
        else:
            lc = None
            rc = None

        leftNode = _BTreeNode(lv, lc)
        rightNode = _BTreeNode(rv, rc)

        if self.parent:
            self.parent.add(tree, medianVal, None, (leftNode, rightNode))
        else:
            # create new root and increment the tree depth
            newRoot = _BTreeNode([medianVal], [leftNode, rightNode])
            leftNode.parent = newRoot
            rightNode.parent = newRoot
            tree.root = newRoot
            tree.height += 1
            tree.size += 1

    def add(self, tree, val, slot=None, childNodes=None):

        assert (self.children is None or childNodes)

        innerNode = self.children is not None
        if innerNode:
            assert (childNodes and len(childNodes) == 2)
        else:
            assert (childNodes is None)

        if slot is None:
            slot = bisect.bisect_left(self.values, val)

        if len(self.values) < tree.max_values:
            self.values.insert(slot, val)
            tree.size += 1
            if childNodes:

                for i in childNodes:
                    i.parent = self
                self.children[slot:slot + 1] = childNodes

            # estamos hechos
            return True

        self._split_node(tree, val, slot, childNodes)
        return True

    def min_value(self, slot=0):
        if self.children:
            return self.children[slot].min_value()
        return self.values[0], self, 0

    def max_value(self, slot=None):
        if slot is None:
            slot = len(self.values) - 1
        if self.children:
            return self.children[slot + 1].max_value()
        return self.values[-1], self, len(self.values) - 1

    def delete(self, tree, val, slot=None):

        innerNode = self.children is not None
        if slot is None:
            assert (slot is not None)
            slot = bisect.bisect_left(self.values, val)

        assert (slot != len(self.values) and self.values[slot] == val)

        if not innerNode:

            del self.values[slot]
            tree.size -= 1
            if len(self.values) < tree.min_values:
                self._rebalance(tree)
        else:

            newSep, node, idx = self.min_value(slot + 1)
            self.values[slot] = newSep
            del node.values[idx]
            tree.size -= 1
            if len(node.values) < tree.min_values:
                node._rebalance(tree)

    def _rebalance(self, tree):
        global sepIdx, ln, rn
        lsibling, rsibling, idx = self.get_siblings()

        assert (rsibling or lsibling or self.parent is None)

        if self.parent is None:
            return

        innerNode = self.children is not None
        if innerNode:
            assert (rsibling is None or rsibling.children is not None)
            assert (lsibling is None or lsibling.children is not None)
        else:
            assert (rsibling is None or rsibling.children is None)
            assert (lsibling is None or lsibling.children is None)

        if not innerNode:
            if rsibling and len(rsibling.values) > tree.min_values:
                sepIdx = idx
                sepVal = self.parent.values[sepIdx]

                self.parent.values[sepIdx] = rsibling.values[0]
                del rsibling.values[0]
                self.values.append(sepVal)
                return
            elif lsibling and len(lsibling.values) > tree.min_values:
                sepIdx = idx - 1
                sepVal = self.parent.values[sepIdx]
                #
                self.parent.values[sepIdx] = lsibling.values[-1]
                del lsibling.values[-1]
                self.values.insert(0, sepVal)
                return

        if lsibling is not None:
            sepIdx = idx - 1
            ln = lsibling
            rn = self
        elif rsibling is not None:
            sepIdx = idx
            ln = self
            rn = rsibling
        else:
            assert (False)

        sepVal = self.parent.values[sepIdx]

        ln.values.append(sepVal)
        ln.values.extend(rn.values)
        del rn.values[:]
        del self.parent.values[sepIdx]
        assert (self.parent.children[sepIdx + 1] is rn)
        del self.parent.children[sepIdx + 1]
        if rn.children:
            ln.children.extend(rn.children)
            for i in rn.children:
                i.parent = ln

        if len(ln.values) > tree.max_values:
            assert (innerNode)
            ln._split_node(tree)

        if len(self.parent.values) < tree.min_values:
            # reequilibrar al padre
            self.parent._rebalance(tree)

        if self.parent.parent is None and not self.parent.values:
            tree.root = ln
            tree.root.parent = None

    def get_siblings(self):
        if not self.parent:
            return (None, None, 0)

        assert (self.parent.children)

        lsibling = None
        rsibling = None
        idx = 0

        for i, j in enumerate(self.parent.children):
            if j is self:
                if i != 0:
                    lsibling = self.parent.children[i - 1]
                if (i + 1) < len(self.parent.children):
                    rsibling = self.parent.children[i + 1]
                idx = i
                break

        return (lsibling, rsibling, idx)


class BTree(object):
    def __init__(self, order):
        if order <= 2:
            raise ValueError("B-tree order must be at least 3")
        self.root = _BTreeNode()
        self.order = order
        self.max_values = order - 1
        self.min_values = self.max_values // 2
        self.height = 1
        self.size = 0

    def __str__(self):
        return 'height: %d items: %d m: %d root: %s' % (
            self.height, self.size,
            self.max_values + 1,
            self.root)

    def add(self, val):

        found, node, slot = self.root.search(val)
        if found:
            return False
        return node.add(self, val, slot, None)

    def delete(self, val):

        found, node, slot = self.root.search(val)
        if not found:
            return False
        return node.delete(self, val, slot)

    def search(self, val):
        return self.root.search(val)[0]

    def min(self):
        return self.root.min_value()[0]

    def max(self):
        return self.root.max_value()[0]


if __name__ == '__main__':
    tree = BTree(5)

    tree.add('moto')
    tree.add('mota')
    tree.add('pedo')
    tree.add('casa')
    tree.add('dedo')
    tree.add('pato')
    tree.add('bano')
    tree.add('tapa')
    tree.add('open')
    tree.add('logo')
    tree.add('rosa')
    tree.add('caja')
    tree.add('pesa')
    tree.add('flor')
    tree.add('fast')
    tree.add('jose')
    tree.add('obed')
    tree.add('lobo')
    tree.add('loro')
    tree.add('lodo')
    tree.root.pretty_print()
    tree.root.graficar(0)
    tree.root.graficarGrap(_BTreeNode.datos)
