"""
用来定义agent的主要的代码
"""


from langchain.tools import tool
import pymysql
from pymysql.cursors import DictCursor
import os
from dotenv import load_dotenv
load_dotenv()
import pymilvus

#全局变量,找到本项目中的根目录
from pathlib import Path
root_path = Path(__file__).parent.parent    #找到根目录了

#定义全局的嵌入向量实例,milvus客户实例
embeddings = None
milvus_client = None

#全局的连接池变量
engine = None

#维护一个全局的agent实例,保证不是每次调用都要重新创建一个agent实例
agent = None

#用来获取嵌入向量对象
def get_embeddings():
    global embeddings
    if embeddings is None:
        from langchain_huggingface import HuggingFaceEmbeddings
        embeddings = HuggingFaceEmbeddings(model=str(root_path / "models" / "bge-m3"))
    return embeddings

#y用来获取milvus客户端实例对象
def get_milvus_client():
    global milvus_client
    if milvus_client is None:
        from pymilvus import MilvusClient
        milvus_client = pymilvus.MilvusClient(uri=os.getenv("MILVUS_HOST"),
                                              token=os.getenv("MILVUS_TOKEN")
                                              )
    return milvus_client

#初始化Mysql连接池
def msql_connnection():
    global engine
    if engine is None:
        from sqlalchemy import create_engine
        engine = create_engine(
            url=f"mysql+pymysql://{os.getenv('MYSQL_USERNAME')}:{os.getenv("MYSQL_PASSWORD")}@{os.getenv("MYSQL_HOST")}:{os.getenv("MYSQL_PORT")}/{os.getenv("MYSQL_DATABASE")}",
            pool_size=15,
        )
    return engine


@tool(description="查询餐厅已标记为特色的主菜。仅在用户要求推荐招牌菜或特色菜时使用，不包含未标记为特色的菜品。")
def search_main_dishes():

    key_name_mapping = {
    "dish_name": "主菜名称",
    "price": "价格",
    "description": "描述",
    "category": "分类",
    "spice_level": "辣度等级",
    "flavor": "口味",
    "main_ingredients": "主要食材",
    "cooking_method": "烹饪方法",
    "is_vegetarian": "是否为素食",
    "allergens": "过敏信息"
 }


    #with 语句叫做上下文管理器（Context Manager）。它的核心作用是：确保资源在用完之后，自动被关闭/释放，无论中间是否发生报错。
    with pymysql.connect(host=os.getenv("MYSQL_HOST"),
                         user=os.getenv("MYSQL_USERNAME"),
                         password=os.getenv("MYSQL_PASSWORD"),
                         port=int(os.getenv("MYSQL_PORT"))) as conn:
        with conn.cursor(DictCursor) as cursor:   #连接（conn）：只负责建立通道，它本身不能直接去查数据。如果传入参数DictCursor会将原本返回的参数元组转换成字典形式
            sql = """
                select
                    dish_name,
                    price,
                    description,
                    category,
                    spice_level,
                    flavor,
                    main_ingredients,
                    cooking_method,
                    is_vegetarian,
                    allergens
                from
                    menu.menu_items
                where
                    is_featured=1
"""
            cursor.execute(sql)
            results =  cursor.fetchall()   #把查询到的数据从数据库拉回到 Python 里。

            #定义json的键, 将数据封装成json
            json_results = []
            for item in results:
                json_item = {}
                for key, value in item.items():
                    json_item[key_name_mapping[key]] = value
                json_results.append(json_item)


            return json_results

@tool(description="根据用户提到的菜品名称、食材、口味、做法或描述进行语义搜索。用户询问具体菜品或食材（例如豆腐、麻婆豆腐、鱼类）时必须使用此工具。")
def user_flavor_search(user_query: str):
    import pymilvus
    from langchain_huggingface import HuggingFaceEmbeddings

    #1. 构建用户query的向量
    embeddings = get_embeddings()

    query_vector = embeddings.embed_query(user_query)

    #2. 连接milvus, 进行向量检索
    client = get_milvus_client()
    #3. 进行向量搜索
    search_res = client.search(
        collection_name="menu_items",
        data=[query_vector],
        anns_field="vector",
        output_fields=["text"],
        limit=3
    )

    #4. 解析搜索结果
    if search_res:
        all_results= search_res[0]  #因为查询的参数只有一个,所以[0]直接获得的就是需要的参数,如果查询阐述不止一个就不能这样用
        #all_results: 列表
        final_result = []

        for item in all_results:
            item_str = item["entity"]["text"]
            final_result.append(item_str)

        return final_result
    else:
        return "在当前库中,没有找到和用户喜好相关的菜品"

from sqlalchemy import text
from pydantic import BaseModel,Field
class ReservationToolArgsInfo(BaseModel):
    num_people:int = Field(description="预约的总人数")
    num_children:int = Field(description="预约的0-2岁儿童人数")
    arrival_time:str = Field(description="预约的到达时间, 格式: YYYY-MM-DD HH")
    seat_preference:str = Field(description="预约的座位偏好, 当用户没有特殊需求时,传递空字符串")
    main_dish_preference:str = Field(description="预约的主菜偏好,当用户没有特殊需求时,传递空字符串")
    comment:str = Field(description="预约的其他备注, 当用户没有特殊需求时, 传递空字符串即可")

@tool(args_schema=ReservationToolArgsInfo,description="用来进行餐厅预定的工具,通过MySQL向数据库中写入数据")
def make_reservation(num_people:int, num_children:int, arrival_time:str, seat_preference:str,main_dish_preference:str,comment:str):
    engine = msql_connnection()
    with engine.connect() as conn:
        sql = text("""
            INSERT INTO reservation_order (num_people,num_children,arrival_time,seat_preference,main_dish_preference,other_comments)
            VALUES (
            :num_people,
            :num_children,
            :arrival_time,
            :seat_preference,
            :main_dish_preference,
            :comment
        )
""")

        #SQLAlchemy 2.x使用命名参数时,已经要传字典形式了
        conn.execute(sql,
    {
        "num_people": num_people,
        "num_children": num_children,
        "arrival_time": arrival_time,
        "seat_preference": seat_preference,
        "main_dish_preference": main_dish_preference,
        "comment": comment,
    },)

        conn.commit() 
        return "预定成功"



async def assistant_query(user_query:str):
    """
    接收来自前端的用户query, 使用agent进行回复
    """
    agent = await create_agent()
    #1. 调用前, 新添加一个system prompt, 让agent感知当前的时间
    from datetime import datetime
    current_date = datetime.now().strftime("%Y-%m-%d")
    time_system_prompt = {"role":"user","content":f"当前日期为:{current_date}"}

    #2. config要怎么去构建, 在实际的生产环境下, 每个用户的每次对话,在后端系统中,都会有一个session_id, 可以拿这个session_id作为thread_id传入进去
    config={"configurable":{"thread_id":"123"}}
    # res = await agent.ainvoke({"messages":[time_system_prompt,{"role":"user","content":"user_query"}]},config=config)

    #3. 如何去调用agent: 通过流式输出
    async for chunk in agent.astream({"messages":[time_system_prompt,{"role":"user","content":user_query}]},config=config,stream_mode="messages"):
        #chunk首先是一个tuple:(AIMessageChunk/ToolMessage,_)
        message = chunk[0]
        if getattr(message, "type", None) not in {"AIMessageChunk", "ai"}:
            continue
        if not getattr(message, "content", ""):
            continue
        # 这个message 需要通过什么方式, 给到谁: 需要通过接口的方式, 给到前端, 然后让前端进行展示
        #需要用到 SSE: Server-Sent Events
        #SSE的数据结构: data: {"type":"token","content":"你好"}

        #快速地将这个方法产出的token, 给到后端接口, 让后端接口去输出给请前端
        import json
        payload = {"content":message.content, "type":"token"}
        payload_str = json.dumps(payload,ensure_ascii=False)
        yield f'data: {payload_str}\n\n'



async def create_agent():
    global agent
    if agent is None:
        from langchain.agents import create_agent
        from langchain_deepseek import ChatDeepSeek
        from langchain_mcp_adapters.client import MultiServerMCPClient
        from langgraph.checkpoint.memory import InMemorySaver   #维护一个短期记忆,是在内存中维护
        from langgraph.checkpoint.sqlite import SqliteSaver     #维护一个长期记忆,是在一个文本中维护,这个是一个同步方法,要使用异步要使用aiosqlite
        import aiosqlite    #维护长期记忆,其实就是sqlite的方式只不过aio是异步方法中使用
        from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
        import sqlite3

        checkpointer = AsyncSqliteSaver(conn=await aiosqlite.connect("./checkpoint.db"))
        client = MultiServerMCPClient(
            connections={
                    "amap_map": {
                        "transport": "sse",
                        "url": "https://mcp.api-inference.modelscope.net/ccaef2a2308042/sse"
                    }
                }
        )

        llm = ChatDeepSeek(model="deepseek-v4-flash")

        with open(str(root_path / "agent" / "prompts" / "system_prompt.txt"),encoding="utf-8") as f:
            system_prompt = f.read()

            mcp_tools = await client.get_tools()

        agent = create_agent(
            model=llm,
            system_prompt=system_prompt,
            tools=[search_main_dishes, user_flavor_search, make_reservation] + mcp_tools,
            checkpointer=checkpointer
        )

    return agent

async def test_agent():
    agent = await create_agent()
    res = await agent.ainvoke({"messages":[{"role":"user","content":"你能为我做什么?"}]},config={"configurable":{"thread_id":"test-1"}})#注意不要忘记配置thread_id因为上下维护也要有名字,不然不知道是哪个上下文
    print(res["messages"][-1].content)

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_agent())
