# Cracked Rotor — Python / Render / GitHub

本目录是 **`cracked_rotor_matlab` 的 Python 移植版**，用于在 **GitHub Actions** 与 **Render** 上运行。  
**不会修改** 原 MATLAB 文件夹：`../cracked_rotor_matlab`。

算法：Table 3 + Fig.10 布置 + 新呼吸函数 `f1,f2` + **4/6 阶谐波平衡**（与 `solve_harmonic_balance.m` 一致）。

## 本地运行

需要 **Python 3.8+**（你当前若是 3.8，会自动安装 `scipy 1.10.x`；推荐 **3.9+** 或 **3.11** 与 CI/Render 一致）。

```bash
cd cracked_rotor_render
pip install -r requirements.txt

# 完整扫频（较慢，数小时级）
python main.py --out output

# CI / 快速验证
python main.py --out output --quick
```

## GitHub Actions

推送本目录到仓库后，`.github/workflows/ci.yml` 会自动：

1. 安装依赖  
2. `python main.py --quick`  
3. 上传 `output/*.png` 为 Artifact  

## Render 部署

1. 新建 **Web Service**，连接本仓库，Root Directory 设为 `cracked_rotor_render`  
2. 使用自带 `Dockerfile` 或 Blueprint `render.yaml`  
3. 启动后访问 `GET /` 健康检查  
4. `POST /generate?quick=true` 生成图片  
5. `GET /figures/fig12_whirl_orbits_node1.png` 下载 PNG  

环境变量：

| 变量 | 说明 |
|------|------|
| `OUTPUT_DIR` | 图片输出目录，默认 `/app/output` |
| `PORT` | Render 注入，默认 10000 |

## 输出图件

| 文件 | 对应文献 |
|------|----------|
| `fig12_whirl_orbits_node1.png` | Fig.12 |
| `fig13a_waterfall.png` | Fig.13(a) |
| `fig14a_waterfall.png` | Fig.14(a) |
| `fig15_paper_spikes_2x2.png` | Fig.15 2×2 竖峰（μ=0.1~0.4） |
| `fig15abc_log_amp_vs_rpm.png` | Fig.15(a,b,c) 对数幅频 |
| `fig16_orbit_grid.png` | Fig.16 |
| `ampfreq_node_curve.png` | 幅频 |

## 目录结构

```
cracked_rotor_render/
  cracked_rotor/     # 核心算法（port）
  main.py            # 命令行
  app.py             # Render API
  Dockerfile
  render.yaml
  .github/workflows/ci.yml
```

## 与 MATLAB 的关系

| MATLAB | Python |
|--------|--------|
| `rotor_params.m` | `cracked_rotor/params.py` |
| `breathing_functions.m` | `cracked_rotor/geometry.py` |
| `assemble_system.m` | `cracked_rotor/fe.py` |
| `solve_harmonic_balance.m` | `cracked_rotor/harmonic_balance.py` |
| `reproduce_paper_HB_fidelity.m` | `cracked_rotor/reproduce.py` |

原 MATLAB 工程仍请在本地用 `reproduce_paper_HB_fidelity` 等脚本运行。
