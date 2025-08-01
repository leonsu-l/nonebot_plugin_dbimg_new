from typing import Union

from nonebot.log import logger
from nonebot.exception import FinishedException
from nonebot.adapters.onebot.v11 import (
    MessageEvent,
    PrivateMessageEvent,
    GroupMessageEvent,
    MessageSegment,
)

from . import tags_search_img
from ...utils import group_cfg, global_cfg
from ...errors import NoImagesFoundError, DerpibooruAPIError

async def _(
    cmd,
    event: Union[MessageEvent, PrivateMessageEvent, GroupMessageEvent],
    tags_str: str,
    onglobal: bool
):
    """处理搜图命令"""
    user_tags = [tag.strip() for tag in tags_str.split(",") if tag.strip()]
    group_tags = group_cfg.get_tags(str(event.group_id)) if isinstance(event, GroupMessageEvent) else []
    global_tags = global_cfg.get_tags()

    all_tags = group_tags + (global_tags if onglobal else []) + user_tags
    tags_list = list(set(all_tags)) # 去重

    logger.info(f"搜索所用tags: {tags_list}")

    try:
        key = global_cfg.get_key()
        img_info = await tags_search_img(tags_list, key)
        logger.success(f"图片信息: {img_info}")

        img_url = img_info["url"]
        img_score = img_info["score"]
        image = MessageSegment.image(img_url)
        img_id = img_url.split('/')[-2] if img_url else None

        at_user = MessageSegment.at(event.user_id)
        await cmd.send(at_user + image + f"id: {img_id}\nscore: {img_score}\ntags: {', '.join(tags_list)}")
        await cmd.finish()
    except NoImagesFoundError as e:
        logger.error(f"无图片: {str(e)}")
        await cmd.finish( str(e) )
    except DerpibooruAPIError as e:
        logger.error(f"Derpibooru API 错误: {str(e)}")
        await cmd.finish("网络错误，请联系bot管理员")
    except FinishedException as e:
        raise
    except Exception as e:
        logger.error(f"Search执行异常: {str(e)}")
        raise