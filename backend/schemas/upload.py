from schemas import ResponseOut


class UploadOut(ResponseOut):
    """图片上传结果：返回可直接用于发布商品的访问地址列表。"""
    urls: list[str]
