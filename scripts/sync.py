#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
心仪蜘蛛源自动同步脚本。

上游 A: 707214981/tvbox-sources  -> spiders/ 目录下的 py/js 爬虫脚本
上游 B: gaotianliuyun/gao         -> js.json 中基于 drpy 的 js 规则源

同步规则:
- 脚本本体复制到本仓库 spiders/ (A) 与 rules-js/ + lib/ (B)
- 生成 TVBox 订阅配置 xinyi.json, 站点显示名按分类命名为 [分类]原名
- 仅复刻 type=3 的 py/js 爬虫; csp_/jar 内置源需要 jar 包, 不纳入
"""

import datetime
import json
import os
import re
import shutil
import subprocess
import tempfile
import urllib.parse

REPO = "xinyicang/xinyi-box"
BRANCH = "main"
RAW = f"https://raw.githubusercontent.com/{REPO}/{BRANCH}"

UPSTREAM_A = {"repo": "707214981/tvbox-sources", "branch": "main", "dir": "spiders"}
UPSTREAM_B = {"repo": "gaotianliuyun/gao", "branch": "master", "file": "js.json"}

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIR_SPIDERS = os.path.join(ROOT, "spiders")
DIR_RULES_JS = os.path.join(ROOT, "rules-js")
DIR_LIB = os.path.join(ROOT, "lib")

EMOJI = re.compile("[\U0001F000-\U0001FAFF\u2600-\u27BF\uFE0F]")

# 分类归一: 追剧/官源/起飞 并入影视; 夸克并入网盘; 音频并入音乐; 其余各自保留
CATEGORY_ALIAS = {
    "追剧": "影视", "影视": "影视", "官源": "影视", "起飞": "影视",
    "短剧": "短剧", "直播": "直播", "动漫": "动漫",
    "音乐": "音乐", "音频": "音乐", "听书": "听书", "少儿": "少儿",
    "体育": "体育", "搜索": "搜索", "磁力": "磁力", "网盘": "网盘",
    "夸克": "网盘", "弹幕": "弹幕", "mv": "MV", "广播": "广播",
    "相声": "相声", "评书": "评书", "格斗": "格斗", "聚合": "聚合",
    "电视": "电视", "其他": "其他",
}


def clean_name(name, fallback=""):
    """去掉 emoji、分类方括号、分隔符、后缀, 得到可区分的干净名称。"""
    if not name:
        name = fallback
    s = EMOJI.sub("", str(name))
    s = re.sub(r"\[[^\]]*\]", "", s)          # [追剧] [js] [飞] 等
    s = s.replace("┃", " ").replace("|", " ")
    s = re.sub(r"\(关梯\)", "", s)
    s = re.sub(r"\.(py|js|txt)$", "", s, flags=re.I)
    s = re.sub(r"[\s·]+", " ", s).strip()
    return s or fallback


def extract_category(raw_name, fallback="其他"):
    """从原名提取分类: B 端优先取竖线前缀, A 端取 [标签]; 再做归一映射。"""
    s = str(raw_name or "")
    parts = re.split(r"[|┃]", s, maxsplit=1)
    if len(parts) == 2:
        token = parts[0]
    else:
        m = re.search(r"\[([^\]]+)\]", s)
        token = m.group(1) if m else None
    if not token:
        return fallback
    token = EMOJI.sub("", token).strip().strip("[]").strip()
    return CATEGORY_ALIAS.get(token) or CATEGORY_ALIAS.get(token.lower()) or (token or fallback)


def split_b_name(raw):
    """B 端名称形如 影视 | 荐片[js], 取竖线后段作为原名。"""
    parts = re.split(r"[|┃]", str(raw or ""), maxsplit=1)
    return parts[1].strip() if len(parts) == 2 else parts[0]


def display_name(category, base):
    """最终显示名: [分类]原名。"""
    return f"[{category}]{base}" if base else f"[{category}]"


def raw_url(section, filename):
    return f"{RAW}/{section}/" + urllib.parse.quote(filename, safe="")


def clone(repo, branch, dst):
    url = f"https://github.com/{repo}.git"
    subprocess.run(
        ["git", "clone", "--depth", "1", "--branch", branch, url, dst],
        check=True,
    )


def reset_dir(path):
    shutil.rmtree(path, ignore_errors=True)
    os.makedirs(path, exist_ok=True)


def sync_upstream_a():
    """同步上游 A 的 py/js 蜘蛛脚本。返回站点条目列表。"""
    reset_dir(DIR_SPIDERS)
    tmp = tempfile.mkdtemp()
    sites = []
    count = 0
    index = {}
    try:
        clone(UPSTREAM_A["repo"], UPSTREAM_A["branch"], os.path.join(tmp, "a"))
        a_src = os.path.join(tmp, "a", UPSTREAM_A["dir"])
        idx_path = os.path.join(a_src, "index.json")
        if os.path.exists(idx_path):
            index = json.load(open(idx_path, encoding="utf-8"))
            shutil.copy2(idx_path, os.path.join(DIR_SPIDERS, "index.json"))

        files = sorted(
            f for f in os.listdir(a_src)
            if f.lower().endswith((".py", ".js"))
        )
        for f in files:
            shutil.copy2(os.path.join(a_src, f), os.path.join(DIR_SPIDERS, f))
            stem = os.path.splitext(f)[0]
            raw = index.get(f, "")
            category = extract_category(raw)
            base = clean_name(raw, stem)
            sites.append({
                "key": "py_" + stem,
                "name": display_name(category, base),
                "type": 3,
                "api": raw_url("spiders", f),
                "searchable": 1,
                "quickSearch": 1,
                "filterable": 1,
            })
        count = len(files)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return sites, count


def sync_upstream_b():
    """同步上游 B 的 drpy js 规则源。返回站点条目列表。"""
    reset_dir(DIR_RULES_JS)
    reset_dir(DIR_LIB)
    tmp = tempfile.mkdtemp()
    sites = []
    count = 0
    try:
        clone(UPSTREAM_B["repo"], UPSTREAM_B["branch"], os.path.join(tmp, "b"))
        b_root = os.path.join(tmp, "b")
        cfg = json.load(open(os.path.join(b_root, UPSTREAM_B["file"]), encoding="utf-8"))

        for site in cfg.get("sites", []):
            if site.get("type") != 3:
                continue
            api = str(site.get("api") or "")
            # csp_ 内置源依赖 jar 包, 跳过; 仅保留 ./lib/ 起步的 drpy js 源
            if api.startswith("csp_") or not api.startswith("./lib/"):
                continue

            api_file = api[len("./lib/"):]
            api_src = os.path.join(b_root, "lib", api_file)
            if not os.path.exists(api_src):
                continue
            shutil.copy2(api_src, os.path.join(DIR_LIB, api_file))

            raw = site.get("name") or api_file
            category = extract_category(raw)
            base = clean_name(split_b_name(raw), api_file)

            entry = {
                "key": "xy_" + str(site.get("key") or api_file),
                "name": display_name(category, base),
                "type": 3,
                "api": raw_url("lib", api_file),
                "searchable": site.get("searchable", 1),
                "quickSearch": site.get("quickSearch", 0),
                "changeable": site.get("changeable", 1),
                "filterable": site.get("filterable", 1),
            }
            for keep in ("style", "timeout", "playerType", "indexs"):
                if keep in site:
                    entry[keep] = site[keep]

            ext = site.get("ext")
            if isinstance(ext, str) and (
                ext.startswith("./js/") or ext.startswith("./lib/")
            ):
                prefix = "./js/" if ext.startswith("./js/") else "./lib/"
                ext_file = ext[len(prefix):]
                ext_dir = "js" if prefix == "./js/" else "lib"
                ext_src = os.path.join(b_root, ext_dir, ext_file)
                if os.path.exists(ext_src):
                    target_dir = DIR_RULES_JS if prefix == "./js/" else DIR_LIB
                    shutil.copy2(ext_src, os.path.join(target_dir, ext_file))
                    entry["ext"] = raw_url(
                        "rules-js" if prefix == "./js/" else "lib", ext_file
                    )

            sites.append(entry)
            count += 1
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return sites, count


def main():
    stats = {
        "synced_at": datetime.datetime.utcnow().isoformat() + "Z",
        "upstreams": {},
    }

    a_sites, a_count = sync_upstream_a()
    stats["upstreams"]["A"] = {"repo": UPSTREAM_A["repo"], "count": a_count}

    b_sites, b_count = sync_upstream_b()
    stats["upstreams"]["B"] = {"repo": UPSTREAM_B["repo"], "count": b_count}

    config = {
        "sites": a_sites + b_sites,
        "parses": [{"name": "Json聚合", "type": 3, "url": "Demo"}],
    }

    with open(os.path.join(ROOT, "xinyi.json"), "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    with open(os.path.join(ROOT, "stats.json"), "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)

    print(f"sites={len(config['sites'])} A={a_count} B={b_count}")


if __name__ == "__main__":
    main()
