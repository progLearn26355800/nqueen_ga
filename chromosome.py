# coding: utf-8


from typing import List
import random


class Chromosome:

    def __init__(self, length: int):
        self.length = length
        self.gene = []
        self.evaluate

    def init_gene(self) -> None:
        self.gene = [random.sample(range(self.length), self.length)]

    def evaluate(self) -> float:
        pass
