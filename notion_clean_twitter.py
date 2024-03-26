from notion_client import Client
class notion_client:
    def __init__(self):
        """
        初始化
        """
        global global_query_results
        global global_notion
        global global_database_id
        global_token = "secret_SGSgYlUHk8knQRLcwJr1alzjzVTwXFwrr0UDBawy0Sw"
        global_database_id = "294cc39bf0424a5ca79de50d76e2f6e1"
        global_notion = Client(auth=global_token)
        global_query_results = global_notion.databases.query(database_id=global_database_id)
        print('开始Notion自动化获取数据...Twitter-Data')
    '''
    插入到子页中
    '''
    def insert_block(self):
        # 获取要插入数据的页面
        blocks=global_notion.blocks
        blocks.children()
        pages=global_notion.pages
        children = global_notion.blocks.children(block_id='d76a06466ea34bfabab68f2e2c8ec2a2')
        # 在页面中添加一个文本块
        new_block = children.add_new(type="text")
        new_block.title = "Your data goes here"

        # 保存更改
        global_notion.submit_transaction()
    """
    获取所有页面
    """
    def get_all_pages_and_duplicate(self,database_id):
        results = []
        start_cursor = None
        while True:
            response = global_notion.databases.query(
                database_id=database_id,
                start_cursor=start_cursor,
                page_size=100,  # Maximum page size
            )
            results.extend(response['results'])
            # temp 处理重复数据-根据唯一值的属性
            self.delete_duplicate_page(results,"正文地址URL")

            start_cursor = response.get('next_cursor')
            if not start_cursor:
                break
        return results
    



    """
    删除页面内容
    """
    def delete_page_content(self, page_id):
        try:
            del_block = global_notion.blocks.delete(block_id=page_id)
            print(f'删除成功:{page_id}')
        except Exception as e:
            print(f'删除失败:{page_id}')
            print(e)
    """
    删除重复的页面-保留最新的页面
    """
    def delete_duplicate_page(self,page_list,property_name):
        property_name_set=set()
        for page in page_list:
            if page["object"] == "page":
                for key, value in page["properties"].items():
                    if key == property_name:
                        # 获取富文本类型的值
                        # text_value=value['rich_text'][0]['text']['content']
                        text_value=value['url']
                        if text_value in property_name_set:
                            print(page["id"])
                            self.delete_page_content(page["id"])
                        else:
                            property_name_set.add(text_value)

"""
1. 清理冗余重复数据
"""
def main():
    client = notion_client()
    client.get_all_pages_and_duplicate(global_database_id)

def insert_block():
    client = notion_client()
    client.insert_block()

if __name__ == '__main__':
    main()
    # insert_block()
    

