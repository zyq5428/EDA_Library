# GitHub SSH 配置

当前工作环境的本仓库已使用 SSH remote：

```text
git@github.com:zyq5428/EDA_Library.git
```

仓库级 `core.sshCommand` 指向 `/home/hero/codex/.ssh/github.conf`，复用 `/home/hero/.ssh/id_ed25519`。配置和私钥不提交到 Git。指定独立配置是为了避开当前环境中系统 SSH 配置文件的权限错误。

Host key 来自 GitHub 官方说明，Ed25519 指纹为：

```text
SHA256:+DiY3wvvV6TuJJhbpZisF/zLDA0zPMSvHdkr4UvCOqU
```

[GitHub 官方 host key](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/githubs-ssh-key-fingerprints)

## 在当前环境验证

当前会话禁止网络 socket，因此尚未验证现有用户密钥是否已登记到 GitHub，也未完成 push。网络可用后执行：

```bash
ssh -F /home/hero/codex/.ssh/github.conf -T git@github.com
git -C /home/hero/codex/EDA_Library ls-remote origin
```

成功时应显示 `Hi zyq5428! You've successfully authenticated...`；GitHub 的 `ssh -T` 成功通常仍返回退出码 1。若显示另一个用户名，应配置属于本账号的密钥后再操作。

若出现 `Permission denied (publickey)`，在 GitHub 的 `Settings → SSH and GPG keys → New SSH key` 中添加以下文件的公钥内容，类型选择 Authentication Key：

```bash
cat /home/hero/.ssh/id_ed25519.pub
```

只添加 `.pub` 内容，私钥始终留在本机。验证后上传本地提交：

```bash
git -C /home/hero/codex/EDA_Library push -u origin main
```

## 换电脑或重新克隆

仓库级 SSH 命令在 `.git/config` 内，不随 GitHub 克隆传播。新电脑应配置自身密钥，不复制上述绝对路径。

已按 GitHub 官方流程配置好 SSH 的电脑，可以直接克隆：

```bash
git clone git@github.com:zyq5428/EDA_Library.git
```

现有克隆切换：

```bash
git remote set-url origin git@github.com:zyq5428/EDA_Library.git
```

[GitHub 官方 SSH 验证说明](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/testing-your-ssh-connection)
