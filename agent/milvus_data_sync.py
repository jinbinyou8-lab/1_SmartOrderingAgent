"""
同步数据到Milvus当中
"""
import os
from dotenv import load_dotenv
load_dotenv()
from  pymysql.cursors import DictCursor
from pymilvus import DataType
import pymysql

def insert_data():

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

    #1. 连接到MySQL数据库, 获取到menu_items当中的所有数据
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
"""
            cursor.execute(sql)
            results =  cursor.fetchall()   #把查询到的数据从数据库拉回到 Python 里。

            #定义json的键, 将数据封装成json
            str_results = []
            for item in results:
                new_result = ""
                for key, value in item.items():
                    new_result += f"{key_name_mapping[key]}:{value}\n"
                str_results.append(new_result)
        
    #2. 连接到Milvus数据库, 获取到client对象
    from pymilvus import MilvusClient
    client = MilvusClient(
        uri=os.getenv("MILVUS_HOST"),
        token=os.getenv("MILVUS_TOKEN")
    )
    if client.has_collection("menu_items"): #如果已经创建过了需要删掉再创建,不然执行了第一次之后第二次没办法执行
         client.drop_collection("menu_items")   

    #3. 创建collection

    schema = MilvusClient.create_schema(
        auto_id = True
    ).add_field(
        field_name = "id",
        datatype = DataType.INT64,
        is_primary = True
    ).add_field(
        field_name="vector",
        datatype=DataType.FLOAT_VECTOR,
        dim = 1024
    ).add_field(
        field_name="text",
        datatype=DataType.VARCHAR,
        max_length=65535
    )

    index_params = MilvusClient.prepare_index_params()  #建立索引

    index_params.add_index(
        field_name="vector",
        index_type="HNSW",
        metric_type = "L2"
    )

    res = client.create_collection(
        collection_name="menu_items",
        schema=schema,
        index_params=index_params
    )

    #4. 使用embedding模型对menu_items数据进行向量化
    from langchain_huggingface import HuggingFaceEmbeddings
    embedding_model = HuggingFaceEmbeddings(
        model=r"F:\SmartOrderingAgent\models\bge-m3"
    )

    vector_list = embedding_model.embed_documents(str_results)

    #5. 将向量化的结果插入到Milvus当中
    insert_rows=[]
    for vector, str_item in zip(vector_list, str_results):
        insert_rows.append(
            {
                "vector":vector,
                "text":str_item
            }
        )

    insert_res = client.insert(data=insert_rows, collection_name="menu_items")
    print(insert_res)
insert_data()