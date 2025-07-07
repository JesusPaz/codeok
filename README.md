# CodeOK 🤖

Tired of nobody approving your PRs? **Call CodeOK!**

A bot that automatically approves your GitHub Pull Requests. For now it approves them just because, just like everyone else who doesn't really look at your changes.

## What does it do?

- 🚀 **Auto-approves PRs** when you mention it (@codeok)
- 🤖 **No questions asked** - Approves everything instantly
- 🔐 **Secure** - Uses GitHub App authentication
- 🆓 **Open Source** - You only need a GitHub App

## Roadmap 🛣️

- 📊 **Code analysis** - Actually review the code
- 📝 **Smart reports** - Generate useful comments about changes
- 🔍 **Suggestions** - Automatically propose improvements
- 🧠 **AI Integration** - For smarter reviews

## Quick Install

### Docker (Easiest)

```bash
docker run -p 8000:8000 \
  -e GITHUB_APP_ID=your_app_id \
  -e GITHUB_PRIVATE_KEY="$(cat your-private-key.pem)" \
  -e WEBHOOK_SECRET=your_webhook_secret \
  -e TARGET_USERNAME=codeok \
  jesuspaz/codeok:latest
```

### Helm Chart (For Kubernetes)

```bash
helm repo add codeok https://jesuspaz.github.io/codeok
helm install codeok codeok/codeok --set secrets.github.appId="your_app_id"
```

## GitHub App Setup

1. Go to GitHub Settings → Developer settings → GitHub Apps
2. Create new app with Pull Requests permissions (Read & Write)
3. Generate a private key
4. Install the app on your repo
5. Done! Mention @codeok in your PRs

## Required Variables

| Variable | Description |
|----------|-------------|
| `GITHUB_APP_ID` | Your GitHub App ID |
| `GITHUB_PRIVATE_KEY` | Private key (.pem) |
| `WEBHOOK_SECRET` | Webhook secret |
| `TARGET_USERNAME` | Username to mention (e.g. "codeok") |

## How to use?

1. Open a PR
2. Write in the body: "Hey @codeok approve this"
3. BOOM! 💥 Automatically approved

## Contributing

It's open source, contribute! 🎉

- 🐛 [Issues](https://github.com/JesusPaz/codeok/issues)
- 💬 [Discussions](https://github.com/JesusPaz/codeok/discussions)

## License

MIT - Use it however you want 🆓