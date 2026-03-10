"""舆情数据爬取 - 东方财富股吧 + AKShare 新闻备选"""

from __future__ import annotations

import logging

import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class EastMoneyScraper:
    """东方财富股吧爬虫"""

    BASE_URL = "https://guba.eastmoney.com/list,{symbol}.html"
    HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    }

    async def fetch_posts(self, symbol: str, limit: int = 20) -> list[dict]:
        """爬取股吧帖子

        Args:
            symbol: 股票代码，如 000001
            limit: 最大抓取条数

        Returns:
            [{"title": str, "author": str, "url": str, "time": str}, ...]
        """
        url = self.BASE_URL.format(symbol=symbol)
        try:
            async with httpx.AsyncClient(
                headers=self.HEADERS, timeout=15, follow_redirects=True
            ) as client:
                resp = await client.get(url)
                resp.raise_for_status()
        except (httpx.HTTPError, httpx.TimeoutException) as e:
            logger.warning("东方财富股吧请求失败: %s", e)
            return []

        return self._parse_posts(resp.text, limit)

    def _parse_posts(self, html: str, limit: int) -> list[dict]:
        """解析股吧页面 HTML"""
        soup = BeautifulSoup(html, "html.parser")
        posts: list[dict] = []

        # 东方财富股吧帖子行在 class 包含 "listitem" 或 articleh 的元素中
        rows = soup.select(".listitem, .articleh, .normal_post")
        if not rows:
            # 备用选择器：尝试表格行
            rows = soup.select("div.list_item, tr")

        for row in rows[:limit]:
            try:
                # 提取标题和链接
                link_el = row.select_one("a.note, a[href*='/news,']")
                if not link_el:
                    link_el = row.find("a", href=True)
                if not link_el or not link_el.get_text(strip=True):
                    continue

                title = link_el.get_text(strip=True)
                href = link_el.get("href", "")
                if href and not href.startswith("http"):
                    href = f"https://guba.eastmoney.com{href}"

                # 提取作者
                author_el = row.select_one(".author, .l3 a, .col_name a")
                author = author_el.get_text(strip=True) if author_el else "未知"

                # 提取时间
                time_el = row.select_one(".time, .l5, .col_time")
                post_time = time_el.get_text(strip=True) if time_el else ""

                posts.append({
                    "title": title,
                    "author": author,
                    "url": href,
                    "time": post_time,
                })
            except Exception:
                continue

        return posts


class AKShareNewsScraper:
    """AKShare 新闻数据源（备选方案，更稳定）"""

    def fetch_posts(self, symbol: str, limit: int = 20) -> list[dict]:
        """通过 AKShare 获取个股新闻

        Returns:
            [{"title": str, "author": str, "url": str, "time": str}, ...]
        """
        from stock_assistant.data.akshare_source import get_data_source

        ds = get_data_source()
        try:
            df = ds.get_news(symbol)
        except Exception as e:
            logger.warning("AKShare 新闻获取失败: %s", e)
            return []

        posts: list[dict] = []
        for _, row in df.head(limit).iterrows():
            title = str(row.get("新闻标题", row.get("title", "")))
            url = str(row.get("新闻链接", row.get("url", "")))
            source = str(row.get("文章来源", row.get("source", "未知")))
            pub_time = str(row.get("发布时间", row.get("publish_time", "")))

            if title:
                posts.append({
                    "title": title,
                    "author": source,
                    "url": url,
                    "time": pub_time,
                })

        return posts


async def fetch_posts(symbol: str, limit: int = 20) -> list[dict]:
    """统一入口：先尝试东方财富股吧，失败则用 AKShare

    Args:
        symbol: 股票代码
        limit: 最大条数

    Returns:
        帖子列表
    """
    scraper = EastMoneyScraper()
    posts = await scraper.fetch_posts(symbol, limit)

    if not posts:
        logger.info("东方财富股吧无结果，回退到 AKShare 新闻源")
        akshare_scraper = AKShareNewsScraper()
        posts = akshare_scraper.fetch_posts(symbol, limit)

    return posts
