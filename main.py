'''
# 正则表达式生成器 regular expression generator
输入一组字符串，生成满足它们的正则表达式，尽可能保留原信息
正则表达式可以在 https://regexper.com/ 可视化

## 基本流程
1. 分词。将每个字符串（句子）拆分为前后缀、单词、分隔符
2. 分组。按照前后缀和分隔符对拆分结果分组，每组单独生成正则，最后用或符号（|）拼接起来
3. 每组相同位置的单词，按照枚举、数字、字母等分类，生成子正则，和前后缀、分隔符拼接为完整正则

## 实例
输入
apple、banana、$100、$200、...、10 apples、15 apples、https://github.com/madokast/TableInsighter4、https://github.com/aaa/bbb、https://github.com/aaa/...

分组处理
 ┌──────────┐  ┌─────────┐ ┌─────────────┐  ┌──────────────────────────────────────────────────────┐
 │  apple   │  │  $ 100  │ │  10 apples  │  │ https :// github . com / madokast / RegexRuleFinder  |
 │  banana  │  │  $ 200  │ │  15 apples  │  │ https :// github . com / aaa      / go               │
 │          │  │  $ ...  │ │             │  │ https :// github . com / aaa      / bbb              │
 └──────────┘  └─────────┘ └─────────────┘  └──────────────────────────────────────────────────────┘
  
 apple|banana    \$\d+      (10|15)\ apples       https://github\.com/(madokast|aaa)/[a-zA-Z]+

合并
(apple|banana)|(\$\d+)|((10|15)\ apples)|(https://github\.com/(madokast|aaa)/[a-zA-Z]+)
'''
import re
import sys
from typing import Iterable, List

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

    如果 words 过长，支持合并，即 new_word = words[i] + delimiters[i] + words[i+1]
    按照优先级挑选 delimiter，优先级高的先合并，优先级排列如下
    6 多字符分隔符（'--'），如果多字符分隔符存在左右空格（' - '），取出空格再计算优先级
    5 下划线（'_'）
    4 其他单字符分隔符（'-#$%&*+/=|~'）
    4 空格（' '）
    3 句号（'.'）
    2 逗号、感叹号、问号、分号、冒号（',!?:;'）
    1 各类引号（'\'"'）
    0 括号（'()<>{}'）
    '''

    delimiter_priority_map:dict[str, int] = {'_':5, ' ':4, '.':3, ',!?:;':2, '\'"`':1, '()<>{}':0}

    PREFIX_RE = r"^((?:[^0-9a-zA-Z])*)(.*)$"
    WORD_RE = r"((?:[0-9a-zA-Z])*)(.*)"

    def __init__(self, prefix:str, suffix:str, words:List[str], delimiters:List[str]) -> None:
        self.prefix = prefix
        self.suffix = suffix
        self.words = words
        self.delimiters = delimiters

    @classmethod
    def split(cls, sentence:str)->'SentenceSplit':
        origin_sentence = sentence

        m = re.match(cls.PREFIX_RE, sentence)
        prefix, sentence = m.group(1), m.group(2)
        m = re.match(cls.PREFIX_RE, sentence[::-1])
        suffix, sentence = m.group(1)[::-1], m.group(2)[::-1]

        words = []
        delimiters = []
        # sentence is empty or starts and ends with a word [0-9a-zA-Z]
        while len(sentence) != 0:
            # extract the leading [0-9a-zA-Z]*
            m = re.match(cls.WORD_RE, sentence)
            word, sentence = m.group(1), m.group(2)

            assert len(word) > 0
            words.append(word)
            
            # then the remaining sentence is empty or starts with delimiter [^0-9a-zA-Z]
            if len(sentence) == 0:
                break
            
            # extract the leading delimiter
            m = re.match(cls.PREFIX_RE, sentence)
            delimiter, sentence = m.group(1), m.group(2)

            assert len(delimiter) > 0
            delimiters.append(delimiter)

            # the remaining sentence is not empty. It must ends with a word
            assert len(sentence) > 0

        # assert the relation of the lengthes of words and delimiters
        if len(words) > 0:
            assert len(words) == len(delimiters) + 1
        
        # assert the prefix + words joining delimiters + suffix is origin_sentence
        s = SentenceSplit(prefix, suffix, words, delimiters)
        assert s.sentence() == origin_sentence, f"'{s.sentence()}' <> '{origin_sentence}'"

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
        temp = "" if len(self.prefix)==0 else re.escape(self.prefix)
        for i in range(len(self.words)):
            # word need no escape
            temp += self.words[i]
            if i < len(self.delimiters):
                temp += re.escape(self.delimiters[i])
        temp += "" if len(self.suffix)==0 else re.escape(self.suffix)
        return "()" if len(temp) == 0 else temp

    # SentenceSplit 的类型，相同的类型将合并为相同的正则
    def type(self)->str:
        delimiters = "D".join(self.delimiters)
        return f"P{self.prefix}S{self.suffix}D{delimiters}"
    
    def words_num(self)->int:
        return len(self.words)

    def merge(self, target_words_num:int)->'SentenceSplit':
        assert target_words_num > 0
        if self.words_num() <= target_words_num:
            return self
        else:
            delimiter_priority_arr = [SentenceSplit._delimiter_priority(d) for d in self.delimiters]
            max_priority = max(delimiter_priority_arr)
            max_priority_index = delimiter_priority_arr.index(max_priority)

            delimiter = self.delimiters[max_priority_index]
            word1 = self.words[max_priority_index]
            word2 = self.words[max_priority_index+1]
            new_word = word1 + delimiter + word2

            new_words = self.words[:max_priority_index] + [new_word] + self.words[max_priority_index+2:]
            new_delimiters = self.delimiters[:max_priority_index] + self.delimiters[max_priority_index+1:]

            return SentenceSplit(self.prefix, self.suffix, new_words, new_delimiters).merge(target_words_num)

    @classmethod
    def _delimiter_priority(cls, delimiter:str)->int:
        delimiter = delimiter.rstrip()
        if len(delimiter) == 0:
            delimiter = ' '
        if len(delimiter)>1:
            return 6
        else:
            for k,v in cls.delimiter_priority_map.items():
                if delimiter in k:
                    return v
            return 4


    def __str__(self) -> str:
        return self.__repr__()
    
    def __repr__(self) -> str:
        return f"prefix:'{self.prefix}', words:{self.words}, delimiters:{self.delimiters}, suffix:'{self.suffix}'"


class WordClassfier:
    NUM_RE = r"^[1-9]\d*$" # 123
    ZERO_LEADABLE_NUM_RE = r"^\d+$" # 0123
    LOWER_WORD_RE = r"^[a-z]+$" #apple
    FIRST_UPPER_WORD_RE = r"^[A-Z][a-z]*$" # Apple
    UPPER_WORD_RE = r"^[A-Z]+$" # APPLE
    MIX_WORD_RE = r"^[a-zA-Z]+$" # rockRDS 大小写混合
    ALPHABETIC_NUMERIC_RE = r"^[0-9a-zA-Z]+$" # rock2022RDS 大小写+数字
    OTHER_RE = r"^.+$" # 匹配所有，例如中文
    REs = [NUM_RE, ZERO_LEADABLE_NUM_RE, LOWER_WORD_RE, FIRST_UPPER_WORD_RE, UPPER_WORD_RE, MIX_WORD_RE, ALPHABETIC_NUMERIC_RE, OTHER_RE]
    RE_BASIC_LENS = [1, 0, 0, 1, 0, 0, 0, 0]

    ENUM_NUM = 10 # 如果只有 5 种单词，生成枚举
    ENUM_RATIO_THRESHOLD = 0.1 # 如果单词频率达到 0.1，生成枚举。剩余的生成通配正则

    def __init__(self) -> None:
        self.card_map:dict[str, int] = dict() # 单词:出现次数，枚举确认
        self.re_map:dict[str, (int, int, int)] = dict() # 正则:满足次数，单词最短长度、最大长度
        self.word_number = 0 # 单词数量
        self.words = [] # 所有单词

        for r in WordClassfier.REs:
            self.re_map[r] = (0, 10000000, 0)

    def put(self, word:str):
        self.word_number += 1
        self.words.append(word)
        if word in self.card_map:
            self.card_map[word] = self.card_map[word] + 1
        else:
            self.card_map[word] = 1

        for r in WordClassfier.REs:
            if re.match(r, word):
                cnt, min_le, max_le = self.re_map[r]
                self.re_map[r] = (cnt+1, min(len(word), min_le), max(len(word), max_le))
                break
    
    def put_all(self, words:Iterable[str])->'WordClassfier':
        for w in words:
            self.put(w)
        return self
    
    def regex(self, enum:bool = True)->str:
        if enum:
            # 全枚举
            if len(self.card_map) <= WordClassfier.ENUM_NUM:
                temp = []
                for e in self.card_map.keys():
                    e_re = re.escape(e)
                    if "|" in e_re:
                        e_re = "(" + e_re + ")"
                    temp.append(e_re)
                return "(" + "|".join(temp) + ")"
            
            # 部分枚举
            enums = set()
            for val, cnt in self.card_map.items():
                if (cnt/self.word_number) > WordClassfier.ENUM_RATIO_THRESHOLD:
                    enums.add(val)
            if len(enums) == 0:
                return self.regex(False)
            else:
                remain = WordClassfier().put_all((w for w in self.words if w not in enums))
                remain_re = remain.regex(False)
                enums_re = []
                for e in enums:
                    e_re = re.escape(e)
                    if "|" in e_re:
                        e_re = "(" + e_re + ")"
                    enums_re.append(e_re)
                enum_re = "(" + "|".join(enums_re) + ")"
                return f"({enum_re}|{remain_re})"
        else:
            re_list = []
            for rid in range(len(WordClassfier.REs)):
                r = WordClassfier.REs[rid]
                cnt, min_le, max_le = self.re_map[r]
                basic_len = WordClassfier.RE_BASIC_LENS[rid]
                min_le, max_le = min_le - basic_len, max_le - basic_len

                if cnt > 0:
                    r = r[1:-2] # [1:-1] # 删除前后的 ^$，删除最后的长度限定
                    if min_le == 0:
                        if max_le == 1:
                            r += "?"
                        else:
                            r += "{," + str(max_le) + "}"
                    else:
                        r += "{" + str(min_le) + "," + str(max_le) + "}"

                    re_list.append(r)

            return "|".join(re_list)




def re_finder(sentences: Iterable[str])->List[str]:
    splits_map:dict[str, List[SentenceSplit]] = dict()
    max_words_num = 0
    for s in sentences:
        split = SentenceSplit.split(s)
        max_words_num = max(split.words_num(), max_words_num)
        t = split.type()
        if t in splits_map:
            splits_map[t].append(split)
        else:
            splits_map[t] = [split]
    
    # while len(splits_map) > 10 or max_words_num > 6:
    #     max_words_num -= 1
    #     new_splits_map:dict[str, List[SentenceSplit]] = dict()
    #     for splits in splits_map.values():
    #         for split in splits:
    #             new_s = split.merge(max_words_num)
    #             t = new_s.type()
    #             if t in new_splits_map:
    #                 new_splits_map[t].append(new_s)
    #             else:
    #                 new_splits_map[t] = [new_s]     
    #     splits_map = new_splits_map
    
    re_strs = []
    for splits in splits_map.values():
        one = splits[0]
        words_num = one.words_num()
        re_words = []
        for words_index in range(words_num):
            words = [split.words[words_index] for split in splits]
            re_word = WordClassfier().put_all(words).regex()
            re_words.append(re_word)
        
        re_str = SentenceSplit(one.prefix, one.suffix, re_words, one.delimiters).regex()
        if "|" in re_str:
            re_str = "(" + re_str + ")"
        # re_str = re_str.replace(r'\ ', r'\s')
        re_strs.append(re_str)


    return "^(" + "|".join(re_strs) + ")$"




if __name__ == '__main__':
    data = open("testdata/d06_condition.txt").readlines()
    data = [s.strip() for s in data]
    re_str = re_finder(data)
    print(re_str)

    for s in data:
        m = re.match(re_str, s)
        print(m)
        if m is None:
            print(f"error {s}", file=sys.stderr)
            print(re_str)
            exit(-1)

    print(re_str)