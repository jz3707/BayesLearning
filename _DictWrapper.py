#!/Users/jiazhen/anaconda3/bin/python3
# coding=utf-8

"""

object dict

"""

import pandas as pd
import copy
import math
import logging

from collections import Counter




DEFAULT_LABEL = "_nolegend_"

class _DictWarpper(object):


    def __init__(self, obj=None, label=None):

        """

        :param obj: Hist, Pmf, Cdf, Pdf, dict, pandas Series, list of pairs
        :param label: string label
        """

        self.label = label if label is not None else DEFAULT_LABEL

        self.d = {}

        self.log = False

        if obj is None:

            return

        # if isinstance(obj, (_DictWarpper, Cdf, Pdf)):
        #
        #     self.label = label if label is not None else obj.label

        if isinstance(obj, (_DictWarpper, dict)):

            self.d.update(obj.items())

        # elif isinstance(obj, (_DictWarpper, Cdf, Pdf)):
        #
        #     self.d.update(obj.items())

        elif isinstance(obj, pd.Series):
            self.d.update(obj.value_counts().iteritems())

        else:
            # list
            self.d.update(Counter(obj))

        if list(self) > 0 and isinstance(self, Pmf):

            self.Normalize()


    def __hash__(self):

        return id(self)


    def __str__(self):

        cls = self.__class__.__name__
        if self.label == DEFAULT_LABEL:

            return "%s(%s)" % (cls, str(self.d))

        else:

            return self.label


    def __repr__(self):

        cls = self.__class__.__name__
        if self.label == DEFAULT_LABEL:
            return '%s(%s)' % (cls, repr(self.d))
        else:
            return '%s(%s, %s)' % (cls, repr(self.d), repr(self.label))


    def __eq__(self, other):

        try:
            return self.d == other.d

        except AttributeError:

            return False

    def __len__(self):

        return len(self.d)

    def __iter__(self):

        return iter(self.d)


    def iterkeys(self):

        """
        iterator over key
        :return:
        """

        return iter(self.d)


    def __contains__(self, item):

        return item in self.d


    def __getitem__(self, item):

        return self.d.get(item)


    def __setitem__(self, key, value):

        self.d[key] = value


    def __delitem__(self, key):

        del self.d[key]


    def Copy(self, label=None):

        """
        浅拷贝
        如果要深拷贝, 使用 copy.deepcopy
        :param label:
        :return:
        """

        new = copy.copy(self)
        new.d = copy.copy(self.d)
        new.label = label if label is not None else self.label

        return new




    def Scale(self, factor):

        """

        乘以 factor
        :param factor:
        :return:
        """

        new = self.Copy()
        new.d.clear()

        for val, prob in self.Items():

            new.Set(val * factor, prob)

        return new


    def Log(self, m=None):

        """
        log概率
        删除了概率为0 的项

        正则化, 最大的log概率为0

        :param m:
        :return:
        """

        if self.log:

            raise ValueError("Pmf/Hist already under a log transform")

        self.log = True

        if m is None:

            m = self.MaxLike()

        for x, p in self.d.items():

            if p:

                self.Set(x, math.log(p / m))

            else:
                self.Remove(x)


    def Exp(self, m=None):

        """

        指数概率


        :param m: 将 ps 取幂之前多少位
        :return:
        """


        if not self.log:

            raise ValueError("Pmf/Hist not under a log transform")

        self.log = False

        if m is None:

            m = self.MaxLie()

        for x, p in self.d.items():

            self.Set(x, math.exp(p - m))


    def GetDict(self):

        return self.d

    def SetDict(self, d):

        self.d = d

    def Values(self):

        return self.d.keys()

    def Items(self):
        """Gets an unsorted sequence of (value, freq/prob) pairs."""
        return self.d.items()


    def SortedItems(self):

        """

        获取一个排序号的 value prob 对

        :return:
        """

        def isnan(x):

            """

            :param x:
            :return:
            """

            try:
                return math.isnan(x)

            except TypeError:

                return False


        if any([isnan(x) for x in self.Values()]):

            msg = "Keys contain Nan, may not not sort correctly"

            logging.warning(msg)


    def Render(self, **options):

        """

        生成序列

        :param options:
        :return:
        """

        return  zip(*self.SortedItems())


    # def MakeCdf(self, label=None):
    #     """Makes a Cdf."""
    #     label = label if label is not None else self.label
    #     return Cdf(self, label=label)


    def Print(self):

        for val, prob in self.SortedItems():

            print(val, prob)


    def Set(self, x, y=0):
        """


        :param x:
        :param y:
        :return:
        """

        self.d[x] = y


    def Incr(self, x, term=1):

        """

        :param x:
        :param term:
        :return:
        """

        self.d[x] = self.d.get(x, 0) + term


    def Mult(self, x, factor):

        """

        :param x:
        :param factor:
        :return:
        """

        self.d[x] = self.d.get(x, 0) * factor


    def Remove(self, x):

        """

        :param x:
        :return:
        """

        del self.d[x]


    def Total(self):

        """

        total prob

        :return:
        """

        total = sum(self.d.values())

        return total


    def MaxLike(self):

        """
        返回 map 中最大的概率值
        :return:
        """

        return max(self.d.values())


    def Largest(self, n=10):

        """
        返回最大的前 n 个概率项
        :return:
        """

        return sorted(self.d.items(), reverse=True)[:n]


    def Smallest(self, n=10):

        """
        最小的前 n 项
        :param n:
        :return:
        """

        return sorted(self.d.items(), reverse=False)[:n]

