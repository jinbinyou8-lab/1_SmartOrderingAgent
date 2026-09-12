from redis import Redis


def redis_commmand_demo1():
    """
    redis相关的命令demo演示
    """



    #1.获取到client对象

    client = Redis.from_url("redis://localhost:6379",decode_responses=True)

    #2. 使用client对象, 执行一些命令

    ##2.1 执行set命令, 创建一个value类型的string的key-value键值对
    client.set("name","张三")

    #2.2 执行get命令, 获取到key为name的value
    name = client.get("name")
    print(name)

    #2.3 创建一个value为hash map 的 key-value对
    client.hset(
        "faq:items:address:test",
        mapping={
            "question":"地址是多少?",
            "answer":"北京市海淀区"
        }
    )

    #2.4 获取到某一个key所对应hash map
    faq_item = client.hgetall("faq:items:address:test")
    print(faq_item)

    #2.5 set其它相关的命令
    #添加了一个key=faq:items value={"address","phone","email"}的一个key-value对
    client.sadd(
          "faq:items",
          "addres","phone","email"
    )
    #result就是key=faq:items对应的value集合
    result = client.smembers(
          "faq:items"
    )
    print(result)


def redis_commmand_demo2():
       #1.获取到client对象
    
        client = Redis.from_url("redis://localhost:6379",decode_responses=True)

        #2. 通过client, 获取到pipeline对象, pipeline的作用是将客户端要发送的命令集中在一起,一同发往服务器进行解析,节省了每次一个命令就要发送一次浪费时间

        pipeline = client.pipeline()

        #3. 使用pipeline声明, 需要执行的命令
        pipeline.set("name2","张三")

        pipeline.hset(
            "faq:items:phone:test",
            mapping={
                  "question":"手机号是多少?",
                  "answer":"13800000000"
            }
        )

        #4. 执行pipeline中的命令
        results = pipeline.execute()
        print(results)

redis_commmand_demo1()