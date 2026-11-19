# xinyi-box · 心仪蜘蛛源合集

自动同步上游 TVBox 蜘蛛（py / drpy js）爬虫规则，订阅配置内站点显示名统一加 **心仪·** 前缀。

## 订阅地址

```text
https://raw.githubusercontent.com/xinyicang/xinyi-box/main/xinyi.json
```

在 TVBox / 影视壳子的「订阅配置 / 配置地址」里粘贴上面这条地址即可。

## 上游来源

| 编号 | 上游仓库 | 同步内容 | 本仓库目录 |
| --- | --- | --- | --- |
| A | [707214981/tvbox-sources](https://github.com/707214981/tvbox-sources) | `spiders/` 下的 `.py` / `.js` 爬虫脚本 | `spiders/` |
| B | [gaotianliuyun/gao](https://github.com/gaotianliuyun/gao) | `js.json` 中基于 drpy 的 js 规则源 | `rules-js/`、`lib/` |

- 仅复刻 `type=3` 的 py / js 爬虫；`csp_` 内置源依赖 jar 包，不纳入本仓库。
- 上游删除的脚本，下次同步会从本仓库对应目录移除，避免残留失效源。

## 自动同步

- 工作流：`.github/workflows/sync.yml`
- 频率：每天 06:00（UTC+8）自动拉取上游并生成 `xinyi.json`；
- 也可在仓库 **Actions → sync-spiders → Run workflow** 里手动触发一次。

## 目录结构

```text
xinyi-box/
├── xinyi.json            # TVBox 订阅配置（同步脚本自动生成）
├── stats.json            # 上次同步时间与各上游数量
├── spiders/              # 上游 A 的 py/js 蜘蛛脚本 + index.json 名称映射
├── rules-js/             # 上游 B 的 drpy js 规则文件
├── lib/                  # 上游 B 的 drpy 运行库
└── scripts/sync.py       # 同步脚本
```

## 说明与免责

- 本仓库只做脚本镜像与配置聚合，不托管任何影视内容；脚本可用性随上游站点变化，失效属正常现象。
- 请在当地法律法规允许的范围内使用，接入前请自行核验源的合规性与可用性。
