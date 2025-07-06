# Helm Chart Publishing Guide

This guide explains how to publish your Helm chart to GitHub Pages and make it available for public use.

## 📋 Prerequisites

1. **GitHub Repository**: Your repository should be public or have GitHub Pages enabled
2. **GitHub Actions**: Ensure GitHub Actions are enabled for your repository
3. **Helm Chart**: Your chart should be in the `helm/` directory

## 🚀 Setup Steps

### 1. Enable GitHub Pages

1. Go to your repository on GitHub
2. Navigate to **Settings** → **Pages**
3. Under **Source**, select **GitHub Actions**
4. Click **Save**

### 2. Configure Repository Settings

The following files are already configured in your repository:

- `.github/workflows/helm-chart-release.yml` - GitHub Action for chart publishing
- `.github/cr.yaml` - Chart Releaser configuration
- `charts/index.yaml` - Initial chart repository index

### 3. Trigger the First Release

The GitHub Action will automatically run when:
- You push changes to the `helm/` directory on the `main` branch
- You manually trigger it from the Actions tab

To trigger manually:
1. Go to **Actions** tab in your repository
2. Select **Release Helm Chart** workflow
3. Click **Run workflow**
4. Select the `main` branch
5. Click **Run workflow**

## 📦 What Happens During Release

1. **Chart Packaging**: The action packages your Helm chart into a `.tgz` file
2. **GitHub Release**: Creates a GitHub release with the chart package
3. **Index Update**: Updates the Helm repository index
4. **Pages Deployment**: Deploys the chart repository to GitHub Pages

## 🎯 Using Your Published Chart

Once published, users can add your chart repository and install your chart:

### Add Repository

```bash
helm repo add codeok https://jesuspaz.github.io/codeok
helm repo update
```

### Install Chart

```bash
# Development installation
helm install my-codeok codeok/codeok \
  --set secrets.github.appId="your_app_id" \
  --set secrets.github.privateKey="$(cat your-private-key.pem)" \
  --set secrets.webhook.secret="your_webhook_secret"

# Production installation
helm install my-codeok codeok/codeok \
  --values values-production.yaml \
  --set externalSecrets.enabled=true
```

### Search Available Charts

```bash
helm search repo codeok
```

## 🔄 Updating Your Chart

To release a new version of your chart:

1. **Update Chart Version**: Edit `helm/codeok-webhook/Chart.yaml`
   ```yaml
   version: 0.2.0  # Increment this
   appVersion: "1.1.0"  # Update if app version changed
   ```

2. **Commit and Push**: 
   ```bash
   git add helm/codeok-webhook/Chart.yaml
   git commit -m "chore: bump chart version to 0.2.0"
   git push origin main
   ```

3. **Automatic Release**: The GitHub Action will automatically:
   - Package the new version
   - Create a new GitHub release
   - Update the chart repository index

## 📊 Monitoring Releases

### Check GitHub Actions

1. Go to **Actions** tab
2. Monitor the **Release Helm Chart** workflow
3. Check for any failures or warnings

### Verify GitHub Pages

1. Go to **Settings** → **Pages**
2. Check that the site is published at `https://jesuspaz.github.io/codeok`
3. Visit the URL to see your chart repository

### Check Releases

1. Go to **Releases** tab
2. Verify that new releases are created for each chart version
3. Check that the chart `.tgz` files are attached

## 🛠️ Troubleshooting

### Common Issues

1. **GitHub Pages Not Enabled**
   - Solution: Enable GitHub Pages in repository settings

2. **Chart Packaging Fails**
   - Check `helm/codeok-webhook/Chart.yaml` for syntax errors
   - Ensure all required fields are present

3. **Release Creation Fails**
   - Check GitHub token permissions
   - Ensure the repository has proper access

4. **Index Update Fails**
   - Check that the `gh-pages` branch exists
   - Verify GitHub Pages is configured correctly

### Debug Commands

```bash
# Test chart locally
helm lint helm/codeok-webhook/
helm template test helm/codeok-webhook/

# Package chart manually
helm package helm/codeok-webhook/

# Test installation locally
helm install test-release ./codeok-0.1.0.tgz --dry-run
```

## 📝 Chart Repository Structure

After publishing, your chart repository will have this structure:

```
https://jesuspaz.github.io/codeok/
├── index.yaml                    # Chart repository index
├── codeok-0.1.0.tgz             # Chart package v0.1.0
├── codeok-0.2.0.tgz             # Chart package v0.2.0
└── ...                          # Future versions
```

## 🔐 Security Considerations

1. **Chart Signing**: Consider signing your charts for production use
2. **Dependency Scanning**: Regularly scan chart dependencies
3. **Version Pinning**: Use specific versions in production
4. **Access Control**: Monitor who can push to your chart repository

## 📚 Additional Resources

- [Helm Chart Best Practices](https://helm.sh/docs/chart_best_practices/)
- [Chart Releaser Action](https://github.com/helm/chart-releaser-action)
- [GitHub Pages Documentation](https://docs.github.com/en/pages)
- [Helm Repository Guide](https://helm.sh/docs/topics/chart_repository/)

## 🎉 Next Steps

1. **Documentation**: Add comprehensive documentation to your chart
2. **Testing**: Set up automated testing for your chart
3. **Monitoring**: Add monitoring and alerting for your published charts
4. **Community**: Share your chart with the community

Your Helm chart is now ready to be published! 🚀 