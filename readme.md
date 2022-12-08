# 正则表达式生成器 regular expression generator
输入一组字符串，生成满足它们的正则表达式，尽可能保留原信息
正则表达式可以在 https://regexper.com/ 可视化

## 基本流程
1. 分词。将每个字符串（句子）拆分为前后缀、单词、分隔符
2. 分组。按照前后缀和分隔符对拆分结果分组，每组单独生成正则，最后用或符号（|）拼接起来
3. 每组相同位置的单词，按照枚举、数字、字母等分类，生成子正则，和前后缀、分隔符拼接为完整正则

## 实例
输入
```
apple
banana
$100
$200
$...
10 apples
15 apples
https://github.com/madokast/TableInsighter4
https://github.com/aaa/bbb
https://github.com/aaa/...
```
分组处理
```
 ┌──────────┐  ┌─────────┐ ┌─────────────┐  ┌──────────────────────────────────────────────────────┐
 │  apple   │  │  $ 100  │ │  10 apples  │  │ https :// github . com / madokast / RegexRuleFinder  |
 │  banana  │  │  $ 200  │ │  15 apples  │  │ https :// github . com / aaa      / go               │
 │          │  │  $ ...  │ │             │  │ https :// github . com / aaa      / bbb              │
 └──────────┘  └─────────┘ └─────────────┘  └──────────────────────────────────────────────────────┘
  
 apple|banana    \$\d+      (10|15)\ apples       https://github\.com/(madokast|aaa)/[a-zA-Z]+
```
合并
```
^((apple|banana)|(\$\d+)|((10|15)\ apples)|(https://github\.com/(madokast|aaa)/[a-zA-Z]+))$
```