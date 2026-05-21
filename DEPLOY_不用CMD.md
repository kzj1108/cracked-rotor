# 不用 CMD：只用 GitHub + Render

## 一、把代码放到 GitHub（网页即可）

### 方式 A：GitHub 网站上传（最简单）

1. 登录 https://github.com → **New repository**
2. 仓库名例如 `cracked-rotor-render`，选 **Public**，创建
3. 进入仓库 → **Add file** → **Upload files**
4. 把本机文件夹 **`cracked_rotor_render` 里的全部内容** 拖进去上传（含 `.github`、Dockerfile、`cracked_rotor` 等）
5. **Commit changes**

> 注意：仓库根目录应直接是 `main.py`、`app.py`、`cracked_rotor/`，不要多包一层 `cracked_rotor_render` 文件夹。若你上传的是外层文件夹，Render 的 Root Directory 要填 `cracked_rotor_render`。

### 方式 B：Cursor / VS Code 源代码管理

1. 左侧 **源代码管理** → **初始化仓库**
2. 全选提交 → **发布到 GitHub**
3. 无需打开 cmd

---

## 二、GitHub Actions 自动出图（推荐，不用本机 Python）

1. 推送完成后，打开仓库 **Actions** 标签
2. 左侧选 **Reproduce figures** → 看到绿色 ✓ 表示成功
3. 点进该次运行 → 页面底部 **Artifacts** → 下载 **paper-figures**（zip，内含全部 PNG）

也可手动再跑一遍：

- **Actions** → **Reproduce figures** → **Run workflow** → Run

全程在浏览器完成，**不需要 cmd**。

---

## 三、Render 部署（浏览器操作）

1. 登录 https://render.com
2. **New +** → **Blueprint**（或 **Web Service**）
3. **Connect GitHub** → 选刚建的仓库
4. 若仓库根就是本工程：Root Directory **留空**  
   若在 monorepo 子目录：Root Directory 填 `cracked_rotor_render`
5. Render 会识别 `render.yaml` 或 `Dockerfile`，点 **Apply / Create**

部署成功后记下网址，例如：`https://cracked-rotor-figures.onrender.com`

### 在浏览器里出图、下图（不用 cmd）

| 操作 | 浏览器地址 |
|------|------------|
| 健康检查 | `https://你的域名/` |
| API 文档（可点按钮试） | `https://你的域名/docs` |
| 快速出图（推荐先试） | `https://你的域名/generate?quick=true` |
| 下载某张图 | `https://你的域名/figures/fig15abc_log_amp_vs_rpm.png` |

在地址栏打开 **`/generate?quick=true`** 后等待页面返回 JSON（可能要几分钟）。返回里的 `files` 列出已生成文件名，再用 `/figures/文件名` 打开或右键另存。

> **说明**：Render 免费实例 HTTP 请求有时间上限，完整扫频 `quick=false` 可能超时。**出图优先用 GitHub Actions 下载 Artifact**；Render 适合演示 API 与在线查看 quick 结果。

---

## 四、推荐流程（零 cmd）

```
上传 GitHub → Actions 自动跑 → 下载 Artifact 里的 PNG
                ↓（可选）
         Render 连同一仓库 → 浏览器打开 /docs 或 /generate?quick=true
```

MATLAB 工程 `cracked_rotor_matlab` **不必上传**，也**不会被修改**。

---

## 五、常见问题

| 问题 | 处理 |
|------|------|
| Actions 没出现 | 确认上传了 `.github/workflows/ci.yml`，且分支是 `main` 或 `master` |
| Artifact 为空 | 打开失败的那次运行，看红色日志 |
| Render 一直转圈 | 先用 `quick=true`；或只用 GitHub Actions 出图 |
| 仓库在子目录 | Render Root Directory 填子目录名 |
