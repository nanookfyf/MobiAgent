from huggingface_hub import snapshot_download

# 下载特定文件夹
snapshot_download(
    repo_id="IPADS-SAI/Chinese-Mobile-Use",
    repo_type="dataset",
    local_dir="./chinese-mobile-use-data",
    allow_patterns="sft/normal/*",  # 只下载指定文件夹的内容
    # 例如：allow_patterns="raw_data/*" 或 allow_patterns="processed/*"
)