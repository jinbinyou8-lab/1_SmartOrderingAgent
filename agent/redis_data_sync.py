"""
将FAQ数据, 导入Redis中, 用于后续查询
"""


FAQ_ITEMS = [
    {
        "id":"address",
        "question": "地址是什么",
        "answer": "北京市东城区东四十二条3号"
    },
    {
        "id":"phone",
        "question": "大堂电话是什么",
        "answer": "我们的电话是:010-87621252, 欢迎您致电"
    },
    {
        "id": "work_time",
        "question": "营业时间",
        "answer": "我们的营业时间如下:周日至周四：早10点至晚21点，周五周六：早10点至晚23点"
    },   
]

def sync_faq_items_to_redis():
    """
    将FAQ_ITEMS中的数据, 同步到Redis中
    """

    #1. 获取到client和pipeline对象
    from redis import Redis
    client = Redis.from_url("redis://localhost:6379",decode_responses=True)
    pipeline = client.pipeline()
    #2. 使用pipeline, 将所有数据, 批量写到Redis的 hash map当中, 以及将所有的keys全部存到set里面去

        #备注: 当前项目比较简单, 实现一个FAQ V1.0版本: 全量比对
        #全量比对: 当用户Query来了之后, 需要把所有的faq questions都从redis里面读出来
        #然后和用户的query去做一个相似度计算, 取出相似度最高的top_k个问题

        #后面如何从redis中得知, 我们有哪些key呢?
            #方式一:redis给我们提供了一个命令: keys pattern(类似于正则匹配的一个表达式), 可以通过这个命令获取到redis中有哪些faq的键
                #但是这种方式不能用: keys命令对服务端的压力很大,占用很多资源 
    # all_faq_keys = client.keys("faq:items:*")     


            #方式二: 单独创建一个set, 来存储所有的faq的key
                #每次增加一个新的faq_item的时候, 就往这个set中添加一个元素.当前,我们就使用这种方案
    #faq:items:address, faq:items:phone... 可以直接通过faq:items:*获取到所有这个路径下的key



#     all_faq_keys = client.smembers("faq:items")

#     for faq_item in all_faq_keys:
#         pipeline.hgetall(faq_item)

#     all_faq_items = pipeline.execute()

#     for faq_item in all_faq_items:


# def _get_similarity_score(query:str,faq_question:str)->float:
    
    for faq_item in FAQ_ITEMS:
        #1. 将数据写入到hash map中
        key = f"faq:items:{faq_item['id']}"
        pipeline.hset(
            name = key,
            mapping={
                "question":faq_item["question"],
                "answer":faq_item["answer"]
            }
        )

        #2. 将它的key添加到faq:items所对应的set当中
        pipeline.sadd(
            "faq:all_items",
            key
        )

        #3. 指定pipeline
        result = pipeline.execute()
        print(result)


        #查看一下是否有取到所有的keys
        all_faq_keys = client.smembers("faq:all_items")
        print(all_faq_keys)

sync_faq_items_to_redis()