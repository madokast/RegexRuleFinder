import re
from typing import Iterable, List

PREFIX_RE = r"^((?:[^0-9a-zA-Z])*)(.*)$"
WORD_RE = r"((?:[0-9a-zA-Z])*)(.*)"

class SentenceSplit:
    '''
    将一个句子按照分隔符切开，分隔符是 [^0-9a-zA-Z]+ 除了字符数字外任意字符及其组合
    
    如果分隔符在句子的开头或者结尾，则记为前缀 prefix 和后缀 suffix
    去除前后缀的句子按照 "单词 + 分隔符 + 单词 + 分隔符 + ... + 单词" 形式
    单词和分隔符依次存放在列表 words 和 delimiters 中
    
    举例
    print(SentenceSplit.split("apple")) # prefix:'', words:['apple'], delimiters:[], suffix:''
    print(SentenceSplit.split("0xaff4")) # prefix:'', words:['0xaff4'], delimiters:[], suffix:''
    print(SentenceSplit.split("2022/12/08 11:39")) # prefix:'', words:['2022', '12', '08', '11', '39'], delimiters:['/', '/', ' ', ':'], suffix:''
    print(SentenceSplit.split("2022年12月8日 11点48分")) # prefix:'', words:['2022', '12', '8', '11', '48'], delimiters:['年', '月', '日 ', '点'], suffix:'分'
    print(SentenceSplit.split("voluntary non-profit - private")) # prefix:'', words:['voluntary', 'non', 'profit', 'private'], delimiters:[' ', '-', ' - '], suffix:''
 
    print(SentenceSplit.split("110 apples")) # prefix:'', words:['110', 'apples'], delimiters:[' '], suffix:''
    print(SentenceSplit.split("79%")) # prefix:'', words:['79'], delimiters:[], suffix:'%'
    print(SentenceSplit.split("!@#$%")) # prefix:'!@#$%', words:[], delimiters:[], suffix:''
    print(SentenceSplit.split("abc!@#$%")) # prefix:'', words:['abc'], delimiters:[], suffix:'!@#$%'

    print(SentenceSplit.split("  _ _-- apple-- b123 _-_ 0123 __ --")) # prefix:'  _ _-- ', words:['apple', 'b123', '0123'], delimiters:['-- ', ' _-_ '], suffix:' __ --'

    '''
    def __init__(self, prefix:str, suffix:str, words:List[str], delimiters:List[str]) -> None:
        self.prefix = prefix
        self.suffix = suffix
        self.words = words
        self.delimiters = delimiters

    @staticmethod
    def split(sentence:str)->'SentenceSplit':
        prefix = None
        suffix = None
        words = []
        delimiters = []

        origin_sentence = sentence

        prefix = re.match(PREFIX_RE, sentence).group(1)
        sentence = re.match(PREFIX_RE, sentence).group(2)
        suffix = re.match(PREFIX_RE, sentence[::-1]).group(1)[::-1]
        sentence = re.match(PREFIX_RE, sentence[::-1]).group(2)[::-1]


        # sentence is empty or starts and ends with a word [0-9a-zA-Z]
        while len(sentence) != 0:
            # extract the leading [0-9a-zA-Z]*
            word = re.match(WORD_RE, sentence).group(1)
            sentence = re.match(WORD_RE, sentence).group(2)

            assert len(word) > 0
            words.append(word)
            
            # then the remaining sentence is empty or starts with delimiter [^0-9a-zA-Z]
            if len(sentence) == 0:
                break
            
            # extract the leading delimiter
            delimiter = re.match(PREFIX_RE, sentence).group(1)
            sentence = re.match(PREFIX_RE, sentence).group(2)

            assert len(delimiter) > 0
            delimiters.append(delimiter)

            # the remaining sentence is not empty. It must ends with a word
            assert len(sentence) > 0
        
        # assert the prefix + words joining delimiters + suffix is origin_sentence
        s = SentenceSplit(prefix, suffix, words, delimiters)
        assert s.sentence() == origin_sentence

        return s

    # origin sentence
    def sentence(self)->str:
        temp = self.prefix
        for i in range(len(self.words)):
            temp += self.words[i]
            if i < len(self.delimiters):
                temp += self.delimiters[i]
        temp += self.suffix
        return temp
    
    def regex(self)->str:
        temp = "(" + re.escape(self.prefix) + ")"
        for i in range(len(self.words)):
            # word need no escape
            temp += "(" + self.words[i] + ")"
            if i < len(self.delimiters):
                temp += "(" + re.escape(self.delimiters[i]) + ")"
        temp += "(" + re.escape(self.suffix) + ")"
        return temp

    # SentenceSplit 的类型，相同的类型将合并为相同的正则
    def type(self)->str:
        delimiters = "D".join(self.delimiters)
        return f"P{self.prefix}S{self.suffix}D{delimiters}"

    def merge(self, delimiters_size:int)->'SentenceSplit':
        pass

    def __str__(self) -> str:
        return self.__repr__()
    
    def __repr__(self) -> str:
        return f"prefix:'{self.prefix}', words:{self.words}, delimiters:{self.delimiters}, suffix:'{self.suffix}'"


def re_finder(sentences: Iterable[str])->List[str]:

    pass

def _word_re_finder(words: Iterable[str])->List[str]:
    pass


if __name__ == '__main__':
    print(SentenceSplit.split("apple")) # prefix:'', words:['apple'], delimiters:[], suffix:''
    print(SentenceSplit.split("0xaff4")) # prefix:'', words:['0xaff4'], delimiters:[], suffix:''
    print(SentenceSplit.split("2022/12/08 11:39")) # prefix:'', words:['2022', '12', '08', '11', '39'], delimiters:['/', '/', ' ', ':'], suffix:''
    print(SentenceSplit.split("2022年12月8日 11点48分")) # prefix:'', words:['2022', '12', '8', '11', '48'], delimiters:['年', '月', '日 ', '点'], suffix:'分'
    print(SentenceSplit.split("voluntary non-profit - private")) # prefix:'', words:['voluntary', 'non', 'profit', 'private'], delimiters:[' ', '-', ' - '], suffix:''
 
    print(SentenceSplit.split("110 apples")) # prefix:'', words:['110', 'apples'], delimiters:[' '], suffix:''
    print(SentenceSplit.split("79%")) # prefix:'', words:['79'], delimiters:[], suffix:'%'
    print(SentenceSplit.split("!@#$%")) # prefix:'!@#$%', words:[], delimiters:[], suffix:''
    print(SentenceSplit.split("abc!@#$%")) # prefix:'', words:['abc'], delimiters:[], suffix:'!@#$%'

    print(SentenceSplit.split("  _ _-- apple-- b123 _-_ 0123 __ --")) # prefix:'  _ _-- ', words:['apple', 'b123', '0123'], delimiters:['-- ', ' _-_ '], suffix:' __ --'