# GitHub + Render 部署指南（照做即可）

项目目录（只上传这一整个文件夹）：

`C:\Users\86159\.cursor\projects\empty-window\cracked_rotor_render`

**不要**把 `cracked_rotor_matlab` 传上去（MATLAB 留在本机即可）。

---

## 一、上传到 GitHub

### 方式 A：网页上传（不用 cmd）

1. 打开 https://github.com → 登录 → 右上角 **+** → **New repository**
2. 仓库名例如：`cracked-rotor-render`，选 **Public**，**不要**勾选 “Add a README”，点 **Create repository**
3. 进入新仓库 → **Add file** → **Upload files**
4. 打开本机文件夹 `cracked_rotor_render`，**全选里面所有文件和文件夹**（含 `.github`、`cracked_rotor`、`Dockerfile` 等）拖进网页
5. 底部 **Commit changes**

**重要：** 仓库根目录应直接是 `main.py`、`app.py`，**不要**多包一层 `cracked_rotor_render` 文件夹。

### 方式 B：Cursor 发布（不用 cmd）

1. 用 Cursor 打开文件夹 `cracked_rotor_render`
2. 左侧 **源代码管理** → **初始化仓库** → 写提交说明 → **发布到 GitHub**
3. 选 **Public**，创建新仓库

---

## 二、GitHub Actions 自动出图

上传成功后：

1. 打开你的仓库 → 顶部 **Actions**
2. 左侧选 **Reproduce figures**
3. 第一次会自动跑；等出现绿色 **✓**
4. 点进这次运行 → 页面下方 **Artifacts** → 下载 **paper-figures**（zip，里面是全部 PNG）

### 手动再跑一遍

- **Actions** → **Reproduce figures** → 右侧 **Run workflow** → **Run workflow**

### 若 Actions 失败

- 点红色 **✗** 看日志；常见原因：仓库根目录不对（`requirements.txt` 不在根目录）

---

## 三、部署到 Render

### 1. 注册并连接 GitHub

1. 打开 https://render.com → 用 GitHub 登录
2. 授权 Render 访问你的仓库

### 2. 新建 Web 服务

**方法 1 — 用 Blueprint（推荐）**

1. Dashboard → **New +** → **Blueprint**
2. 选刚建的 GitHub 仓库
3. Render 会读仓库里的 `render.yaml`，点 **Apply**
4. 等待部署完成（约 5~15 分钟）

**方法 2 — 手动 Docker**

1. **New +** → **Web Service**
2. 连接同一仓库
3. **Root Directory**：若仓库根就是 `cracked_rotor_render` 内容 → **留空**  
   若整个 `empty-window` 都在仓库里 → 填 `cracked_rotor_render`
4. **Runtime**：Docker
5. **Dockerfile Path**：`Dockerfile`
6. **Instance Type**：Free
7. **Create Web Service**

### 3. 部署成功后怎么用（浏览器即可）

记下网址，例如：`https://cracked-rotor-figures.onrender.com`

| 操作 | 浏览器地址 |
|------|------------|
| 是否正常 | `https://你的域名/` |
| API 文档 | `https://你的域名/docs` |
| **生成图（快速）** | `https://你的域名/generate?quick=true` |
| **生成图（完整，很慢）** | `https://你的域名/generate?quick=false` |
| 下载图 12 | `https://你的域名/figures/fig12_whirl_orbits_node1.png` |
| 下载图 13 | `https://你的域名/figures/fig13a_waterfall.png` |
| 下载图 15 | `https://你的域名/figures/fig15_paper_spikes_2x2.png` |

在地址栏打开 `/generate?quick=true`，等几分钟直到返回 JSON（含 `files` 列表），再用 `/figures/文件名` 看图。

**说明：** Render 免费版 HTTP 请求有时间限制，**完整扫频可能超时**；日常出图优先用 **GitHub Actions 下载 Artifact**。

---

## 四、推荐组合

| 用途 | 用哪个 |
|------|--------|
| 自动出图、下载 zip | **GitHub Actions** |
| 在线 API、给别人访问链接 | **Render** |
| 最像文献、本地调试 | 本机 **MATLAB `RUN_ALL`** |

---

## 五、仓库结构检查（上传前看一眼）

根目录应有：

```
main.py
app.py
requirements.txt
Dockerfile
render.yaml
.github/workflows/ci.yml
cracked_rotor/
```

缺 `.github` 则 Actions 不会出现。

---

## 六、常见问题

| 问题 | 处理 |
|------|------|
| Actions 没有 | 确认 `.github/workflows/ci.yml` 已上传，分支是 `main` 或 `master` |
| Render 构建失败 | 看 Logs；确认 Dockerfile 在 Root Directory 下 |
| `/generate` 一直转圈 | 先用 `quick=true`；或只用 GitHub Actions |
| 图是空的 | 本地先 `python main.py --out output --quick` 测试；已内置模型兜底 |
| 仓库在子目录 | Render **Root Directory** 填 `cracked_rotor_render` |

---

## 七、以后更新代码

1. 改好本机 `cracked_rotor_render` 里的文件  
2. 在 GitHub 网页 **Upload files** 覆盖，或 Cursor **提交并推送**  
3. Actions 自动重跑；Render 若开了 **Auto-Deploy** 会自动重新部署  
