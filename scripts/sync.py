#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
心仪蜘蛛源自动同步脚本。

上游 A: 707214981/tvbox-sources  -> spiders/ 目录下的 py/js 爬虫脚本
上游 B: gaotianliuyun/gao         -> js.json 中基于 drpy 的 js 规则源

同步规则:
- 脚本本体复制到本仓库 spiders/ (A) 与 rules-js/ + lib/ (B)
- 生成 TVBox 订阅配置 xinyi.json, 站点显示名统一加 "心仪·" 前缀
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
            base = clean_name(index.get(f, ""), stem)
            sites.append({
                "key": "py_" + stem,
                "name": "心仪·" + base,
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

            entry = {
                "key": "xy_" + str(site.get("key") or api_file),
                "name": "心仪·" + clean_name(site.get("name"), api_file),
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
