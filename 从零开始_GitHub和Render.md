# 从零开始：GitHub + Render 完整步骤

按顺序做，**不要跳步**。全程可在浏览器完成，不必用 cmd。

本机项目文件夹（所有要上传的内容）：

`C:\Users\86159\.cursor\projects\empty-window\cracked_rotor_render`

---

## 第 0 步：准备（本机检查）

打开上述文件夹，确认里面有：

- [x] `main.py`
- [x] `app.py`
- [x] `requirements.txt`
- [x] `Dockerfile`
- [x] `render.yaml`
- [x] 文件夹 `cracked_rotor`（里面有多个 `.py`）
- [x] 文件夹 `.github` → `workflows` → `ci.yml`

若缺 `.github`，见本文 **附录 A** 在 GitHub 新建。

---

## 第 1 步：新建 GitHub 仓库

1. 登录 https://github.com
2. 右上角 **+** → **New repository**
3. 填写：
   - **Repository name**：`cracked-rotor`（可自定，英文无空格）
   - **Public**
   - **不要**勾选 “Add a README file”
   - **不要**选 .gitignore / license（避免和上传冲突）
4. 点 **Create repository**

记下仓库地址，例如：`https://github.com/kzj1108/cracked-rotor`

---

## 第 2 步：上传代码（关键：直接放在仓库根目录）

1. 进入刚建的空仓库页面
2. 点 **Add file** → **Upload files**
3. 打开本机 `cracked_rotor_render` 文件夹
4. **全选**下列内容（Ctrl+A 选中文件夹内所有项）拖到浏览器：

   - `main.py`
   - `app.py`
   - `requirements.txt`
   - `Dockerfile`
   - `render.yaml`
   - `README.md`
   - 文件夹 **`cracked_rotor`**
   - 文件夹 **`.github`**（若看不到，见下方「显示隐藏文件」）
   - 其他 `.md` / `.txt` 可有可无

5. **不要**把整个 `cracked_rotor_render` 文件夹拖进去当一层外壳  
   → 上传后 **Code** 页第一行应直接是 `main.py`，而不是 `cracked_rotor_render/main.py`

6. 底部 **Commit changes**

### 显示隐藏文件夹 `.github`（Windows）

- 资源管理器 → **查看** → 勾选 **隐藏的项目**
- 或在本机用 Cursor 左侧文件树把 `.github` 拖进上传区

### 上传成功后 Code 页应类似

```
cracked-rotor/
├── .github/workflows/ci.yml
├── cracked_rotor/
├── main.py
├── app.py
├── requirements.txt
├── Dockerfile
└── render.yaml
```

---

## 第 3 步：GitHub Actions 自动出图

1. 仓库顶栏 → **Actions**
2. 若提示启用 Actions → 点 **I understand my workflows, go ahead and enable them**
3. 左侧应出现 **Reproduce figures**
4. 第一次 push 后通常会自动跑；也可手动：
   - **Reproduce figures** → 右侧 **Run workflow** → **Run workflow**
5. 等待 **5~20 分钟**（绿色 ✓，不是 7 秒就红）
6. 点进该次运行 → 页面下方 **Artifacts** → 下载 **paper-figures**（zip，内含 PNG）

### 若仍是红色失败

点失败记录 → 展开红色步骤，常见原因：

| 日志关键词 | 处理 |
|------------|------|
| `requirements.txt` not found | 第 2 步结构错了，代码不在根目录 → 重做第 2 步 |
| `main.py` not found | 同上 |
| `ModuleNotFoundError` | 确认 `cracked_rotor` 文件夹已上传 |

---

## 第 4 步：部署 Render

1. 打开 https://render.com → **Get Started** → 用 **GitHub** 登录
2. 授权 Render 访问 GitHub
3. **New +** → **Web Service**
4. 选择仓库 **`cracked-rotor`**（你刚建的那个）→ **Connect**
5. 填写：

   | 项 | 值 |
   |---|---|
   | Name | `cracked-rotor-api`（自定） |
   | Region | 选离你近的 |
   | Branch | `main` |
   | Root Directory | **留空**（因为 main.py 在仓库根） |
   | Runtime | **Docker** |
   | Dockerfile Path | `./Dockerfile` |

6. Instance Type 选 **Free**
7. **Create Web Service**
8. 等待 **Build** 和 **Deploy** 变绿（约 5~15 分钟）

### Render 使用（浏览器）

部署完成后有网址，例如：

`https://cracked-rotor-api.onrender.com`

| 操作 | 地址 |
|------|------|
| 健康检查 | `/` |
| API 文档 | `/docs` |
| 生成图（快，推荐） | `/generate?quick=true` |
| 下载图 13 | `/figures/fig13a_waterfall.png` |

打开 `/generate?quick=true` 后等几分钟，返回 JSON 里 `files` 列出 PNG 名，再用 `/figures/文件名` 查看。

---

## 第 5 步：以后更新代码

1. 本机改 `cracked_rotor_render` 里的文件
2. GitHub 仓库 → **Add file** → **Upload files** 覆盖对应文件  
   或 Cursor **源代码管理** → 提交 → 推送
3. Actions 自动重跑；Render 自动重新部署（若开了 Auto-Deploy）

---

## 附录 A：若没有 `.github` 文件夹

在仓库 **Add file** → **Create new file**，文件名输入：

`.github/workflows/ci.yml`

（输入时会自动建文件夹）

粘贴：

```yaml
name: Reproduce figures

on:
  push:
    branches: [main, master]
  workflow_dispatch:

jobs:
  figures:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Generate figures
        run: python main.py --out output --quick

      - name: Upload artifacts
        uses: actions/upload-artifact@v4
        with:
          name: paper-figures
          path: output/*.png
          retention-days: 14
```

**Commit changes**。

---

## 附录 B：若你坚持把代码放在子文件夹

仅当 Code 页是 `cracked_rotor_render/main.py` 时用。

根目录 `.github/workflows/ci.yml` 内容为：

```yaml
name: Reproduce figures

on:
  push:
    branches: [main, master]
  workflow_dispatch:

jobs:
  figures:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: cracked_rotor_render
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Generate figures
        run: python main.py --out output --quick
      - name: Upload artifacts
        uses: actions/upload-artifact@v4
        with:
          name: paper-figures
          path: cracked_rotor_render/output/*.png
          retention-days: 14
```

Render 的 **Root Directory** 填：`cracked_rotor_render`

---

## 附录 C：MATLAB 本地出图（与 GitHub 无关）

```matlab
cd('C:\Users\86159\.cursor\projects\empty-window\cracked_rotor_matlab')
RUN_ALL
```

图片在 `cracked_rotor_matlab\output\`。

---

## 一张表总结

| 平台 | 做什么 | 结果在哪 |
|------|--------|----------|
| GitHub Actions | 自动算图 | Artifacts → paper-figures.zip |
| Render | 网页 API + 在线看图 | `/figures/xxx.png` |
| MATLAB RUN_ALL | 本地最贴近文献 | `output\*.png` |
