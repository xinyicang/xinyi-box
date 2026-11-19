# xinyi-box · 心仪蜘蛛源合集

自动同步上游 TVBox 蜘蛛（py / drpy js）爬虫规则与直播列表，订阅配置内站点显示名按分类命名为 **[分类]原名**（如 `[影视]爱奇艺`、`[短剧]红果短剧`）；直播列表内置在本仓库 `lives/` 目录，与点播共用同一个订阅入口。

## 订阅地址

```text
https://raw.githubusercontent.com/xinyicang/xinyi-box/main/xinyi.json
```

在 TVBox / 影视壳子的「订阅配置 / 配置地址」里粘贴上面这条地址即可。国内 raw 打不开时可套加速前缀，例如：

```text
https://ghfast.top/https://raw.githubusercontent.com/xinyicang/xinyi-box/main/xinyi.json
```

## 上游来源

| 编号 | 上游仓库 | 同步内容 | 本仓库目录 |
| --- | --- | --- | --- |
| A | [707214981/tvbox-sources](https://github.com/707214981/tvbox-sources) | `spiders/` 下的 `.py` / `.js` 爬虫脚本 | `spiders/` |
| B | [gaotianliuyun/gao](https://github.com/gaotianliuyun/gao) | `js.json` 中基于 drpy 的 js 规则源 | `rules-js/`、`lib/` |
| C | [xinyicang/live-sources](https://github.com/xinyicang/live-sources) | `tv/live.txt` 直播列表，清洗后内置快照 | `lives/` |

- 仅复刻 `type=3` 的 py / js 爬虫；`csp_` 内置源依赖 jar 包，不纳入本仓库。
- 上游删除的脚本，下次同步会从本仓库对应目录移除，避免残留失效源。

## 直播

- 直播列表由同步脚本从 `live-sources/tv/live.txt` 拉取、清洗（去空行、修复行尾逗号）后写入本仓库 `lives/xinyi-live.txt`；
- 订阅配置 `lives` 数组指向本仓库内置的这份列表，同名频道的多条线路全部保留；
- 不附加节目单（epg）与台标 logo。

## 分类命名规则

- 分类取自上游原名：A 端取 `[标签]`，B 端取竖线前的分类词；
- `追剧 / 官源 / 起飞` 统一并入 **[影视]**，`夸克` 并入 **[网盘]**，`音频` 并入 **[音乐]**；
- 其余按上游标签各自保留：短剧、直播、动漫、音乐、听书、少儿、体育、搜索、磁力、网盘、弹幕、MV、广播、相声、评书、格斗、聚合、电视等；
- 无法识别分类的条目归为 **[其他]**。

## 自动同步

- 工作流：`.github/workflows/sync.yml`
- 频率：每天 06:00（UTC+8）自动拉取上游并生成 `xinyi.json`；
- 也可在仓库 **Actions → sync-spiders → Run workflow** 里手动触发一次。

## 目录结构

```text
xinyi-box/
├── xinyi.json            # TVBox 订阅配置（同步脚本自动生成，含 lives 与 sites）
├── stats.json            # 上次同步时间与各上游数量
├── lives/                # 内置直播列表快照 xinyi-live.txt
├── spiders/              # 上游 A 的 py/js 蜘蛛脚本 + index.json 名称映射
├── rules-js/             # 上游 B 的 drpy js 规则文件
├── lib/                  # 上游 B 的 drpy 运行库
└── scripts/sync.py       # 同步脚本
```

## 说明与免责

- 本仓库只做脚本镜像、直播链接聚合与配置生成，不托管任何影视内容；脚本与线路可用性随上游站点变化，失效属正常现象。
- 请在当地法律法规允许的范围内使用，接入前请自行核验源的合规性与可用性。
