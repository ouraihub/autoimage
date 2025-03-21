好的，我将帮您使用conda创建Python 3.10的虚拟环境。以下是具体步骤：

1. 创建conda环境：

```bash
# 创建名为ai_image的Python 3.10环境
conda create -n ai_image python=3.10
```

2. 激活环境：

```bash
# 激活环境
conda activate ai_image
```

3. 安装依赖包：

```bash
# 使用pip安装requirements.txt中的包
pip install -r requirements.txt
```

4. 运行应用：

```bash
# 确保环境已激活
streamlit run app.py
```

如果您想要查看或管理conda环境，可以使用以下命令：

```bash
# 列出所有conda环境
conda env list

# 删除环境（如果需要）
conda env remove -n ai_image

# 查看当前环境安装的包
conda list
```

您也可以创建一个`environment.yml`文件来管理conda环境：

```yaml:environment.yml
name: ai_image
channels:
  - defaults
  - conda-forge
dependencies:
  - python=3.10
  - pip
  - pip:
    - streamlit==1.31.1
    - requests==2.31.0
    - Pillow==10.2.0
    - python-dotenv==1.0.1
```

然后可以使用以下命令创建环境：

```bash
conda env create -f environment.yml
```

## 配置说明

本项目需要配置 Cloudflare 凭证才能运行。请按照以下步骤进行配置：

1. 复制示例配置文件：
   ```bash
   cp .env.example .env
   # 或者
   cp .streamlit/secrets.example.toml .streamlit/secrets.toml
   ```

2. 编辑配置文件，填入你的 Cloudflare 凭证：
   - CLOUDFLARE_ACCOUNT_ID：你的 Cloudflare 账户 ID
   - CLOUDFLARE_API_TOKEN：你的 Cloudflare API 令牌

3. 确保配置文件已被 .gitignore 忽略，不会被提交到代码库

## 部署说明

### 本地开发
1. 复制配置示例文件：
   ```bash
   cp .streamlit/secrets.example.toml .streamlit/secrets.toml
   ```
2. 编辑 `.streamlit/secrets.toml`，填入你的 Cloudflare 凭证

### Streamlit Cloud 部署
1. 在 [Streamlit Cloud](https://share.streamlit.io) 创建新的应用
2. 在应用设置中，找到 "Secrets" 部分
3. 添加以下配置：
   ```toml
   CLOUDFLARE_ACCOUNT_ID = "your_account_id"
   CLOUDFLARE_API_TOKEN = "your_api_token"
   ```


