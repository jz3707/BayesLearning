#!/Users/jiazhen/anaconda3/bin/python3
# coding=utf-8

"""

Pmf

"""

import random
import numpy as np
import math

from . import _DictWrapper



class Pmf(_DictWrapper):

    """
    概率质量函数

    值是可 哈希类型
    概率是浮点类型

    概率质量函数不要求正则化

    """

    def Prob(self, x, default=0):

        """
        获取 x 的 概率
        :param x:
        :param default:
        :return:
        """

        return self.d.get(x, default)


    def Probs(self, xs):

        """
        获取序列的概率值
        :param xs:
        :return:
        """

        return [self.Prob(x) for x in xs]


    def Percentile(self, percentage):

        """

        计算给定 Pmf 的百分位数
        这个函数效率不是很高,


        :param percentage: 0 - 100
        :return:
        """

        p = percentage / 100
        total = 0

        for val, prob in sorted(self.Items()):

            total += prob
            if total >= p:
                return val


    def ProbLess(self, x):

        """

        从这个概率质量函数中抽取一个样本小于 x 的概率是多少
        相当于求直方图的面积或者是曲线下面积

        :param x:
        :return:
        """

        if isinstance(x, _DictWrapper):

            return PmfProbLess(self, x)

        else:

            #
            t = [prob for (val, prob) in self.d.items() if val < x]
            return sum(t)


    def ProbEqual(self, x):

        """

        计算从这个 Pmf 中抽取一个样本等于 x 的概率

        :param x:
        :return:
        """

        if isinstance(x, _DictWrapper):

            return PmfProbEqual(self, x)

        else:

            return self[x]


    def Normalize(self, fraction=1):

        """

        正则化 Pmf, 因此所有概率和为 fraction

        :param fraction:
        :return:
        """

        if self.log:

            raise ValueError("Normalize: Pmf is under a log transform")

        total = self.Total()

        if total == 0:

            raise  ValueError("Normalize : total probability is zero")

        factor = fraction / total

        for x in self.d:
            self.d[x] *= factor

        return total

    def Random(self):

        """
        从这个 Pmf 中随机选择一个 element
        这个方法效率不高

        :return:
        """

        target = random.random()
        total = 0

        for x, p in self.d.items():

            total += p
            if total >= target:

                return x


    # def Sample(self, x):
    #
    #     """
    #
    #     从当前分布中生成随机样本
    #
    #     :param x:
    #     :return:
    #     """
    #
    #     return self.MakeCdf().sample()


    def Mean(self):

        """

        计算均值
        :param mu: 如果提供, 计算方差
        :return:
        """

        return sum(p * x for x, p in self.d.items())

    # def Median(self):
    #     """Computes the median of a PMF.
    #     Returns:
    #         float median
    #     """
    #     return self.MakeCdf().Percentile(50)
    #


    def Var(self, mu= one):

        """

        :param mu: 如果提供了则计算方差
        :return:
        """

        if mu is None:

            mu = self.Mean()

        return sum(p * (x - mu) ** 2 for x, p in self.Items())


    def Expect(self, func):

        """
        计算 func 的期望
        :param func:
        :return:
        """

        return np.sum(p * func(c) for x, p in self.Items())


    def Std(self, mu=None):

        """


        :param mu:
        :return:
        """

        if mu is None:

            mu = self.Mean()

        var = self.Var(mu)
        return math.sqrt(var)


    def Mode(self):

        """
        返回最高概率值

        :return:
        """

        _, val = max((prob, val) for val, prob in self.Items())

        return val


    # 最大后验概率
    MAP = Mode

    # 如果分布只包含似然, 峰值就是最大后验估计
    MaximumLikelihood = Mode



    # def CredibleInterval(self, percentage=90):
    #
    #     """
    #
    #     置信区间
    #
    #     :param percentage:
    #         = 90, 计算90%CI
    #
    #     :return:
    #     """
    #
    #     cdf = self.MakeCdf()
    #     return cdf.CredibleInterval(percentage)


    def __add__(self, other):

        """



        :param other:
        :return:
        """

        try:

            return self.AddPmf(other)

        except AttributeError:

            return self.AddConstant(other)

    __radd = __add__


    def AddPmf(self, other):

        """

        从自己和其他 Pmf 来计算和的 Pmf

        :param other:
        :return:
        """

        pmf = Pmf()
        for v1, p1 in self.Items():

            for v2, p2 in other.Items():

                pmf[v1 + v2] += p1 * p2

        return pmf



    def AddConstant(self, other):

        """

        计算自己的值和常数和的 pmf

        :param other:
        :return:
        """

        if other == 0:

            return self.Copy()

        pmf = Pmf()

        for v1, p1 in self.Items():

            pmf.Set(v1 + other , p1)

        return pmf


    def __sub__(self, other):

        """

        计算当前 pmf 和其他 pmf 差的 pmf

        :param other:
        :return:
        """

        try:
            return self.SubPmf(other)

        except AttributeError:

            return self.AddConstant(-other)


    def SubPmf(self, other):

        """

        计算当前 pmf 和其他 pmf 差的 pmf

        :param other:
        :return:
        """

        pmf = Pmf()

        for v1, p1 in self.Items():

            for v2, p2 in other.Items():

                pmf.Incr(v1 - v2, p1 * p2)

        return pmf


    def __mul__(self, other):

        """

        计算当前 pmf 和其他 pmf 值的乘积的 pmf

        :param other:
        :return:
        """

        try:

            return self.MulPmf(other)

        except AttributeError:

            return self.MulConstant(other)


    def MulPmf(self, other):

        """

        计算当前 pmf 和其他 pmf 值的乘积的 pmf

        :param other:
        :return:
        """

        pmf = Pmf()



        for v1, p1 in self.Items():

            for v2, p2 in other.Items():

                pmf.Incr(v1 * v2, p1 * p2)

        return pmf


    def MulConstant(self, other):

        """

        当前 pmf 乘以一个常数的 pmf

        :param other:
        :return:
        """

        if other == 0:

            return self.Copy()

        pmf = Pmf()

        for v, p in self.Items():

            pmf.Set(v * other, p)

        return pmf


    def __div__(self, other):

        """

        计算当前 pmf 和其他 pmf 除之后的值的 pmf

        :param other:
        :return:
        """

        try:

            return self.DivPmf(other)

        except AttributeError:

            return self.MulConstant(1/other)


    __truediv__ = __div__

    def DivPmf(self, other):

        """

        计算当前 pmf 和其他 pmf 除之后的值的 pmf
        :param other:
        :return:
        """

        pmf = Pmf()

        for v1, p1 in self.Items():

            for v2, p2 in other.Items():

                pmf.Incr(v1 / v2, p1 * p2)

        return pmf


    # def Max(self, k):
    #
    #     """
    #
    #     计算当前分布最大的 k 个 CDF
    #
    #     :param k:
    #     :return:
    #     """
    #
    #     cdf = self.MakeCdf()
    #     cdf.ps **= k
    #     return  cdf






