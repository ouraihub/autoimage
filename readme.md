
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


