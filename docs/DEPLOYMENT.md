# Publish the GitHub-ready application

This handoff is a local repository package. No existing GitHub repository was changed and no public site was deployed. It uses static hosting rather than Streamlit.

## GitHub Pages

1. Extract `python-market-analytics-platform.zip`. Open the enclosed project directory.
2. Put the contents in your intended repository. If replacing an existing project, preserve its prior version on a branch or make a backup first. Include `.github/workflows/`, which some file browsers hide.
3. Commit the included files. Do not upload the ZIP as the application itself. Do not upload raw KLEM archives, live state or credentials.
4. In repository **Settings → Pages → Build and deployment**, select **GitHub Actions**.
5. Open **Actions → Deploy MarketLab → Run workflow** on the intended branch. The workflow runs tests, compiles the selected public dataset, scans public files, and deploys only `dist/`.
6. Open the deployment URL returned by the workflow. Replace the README's pending-live-demo text with that actual URL.

The deployment workflow is manually dispatched so uploading the package cannot unexpectedly replace a live site. Run it again after later approved updates. The separate CI workflow runs on pushes and pull requests. Static assets use relative paths, so project subpaths work without a hard-coded owner or repository name.

[GitHub custom workflow documentation](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages) · [Configuring the publishing source](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site)

## Alternative static hosting

Serve the generated `dist/` directory with any static host. No server-side Python runtime is required after building. Build locally with Python 3.11+ or configure the host's build command as `python -m marketlab build` and publish directory as `dist`.

## Local preview

Double-click `dist/index.html` for an offline preview, or run:

```bash
python -m marketlab build
python -m http.server 8000 --directory dist
```

## Replacing synthetic data

Follow `IMPORT_REAL_DATA.md`, change `research/build-config.json`, and rebuild. Do not relabel the demonstration as real data. A real-data import does not make the fictional settlement fixtures real; that page retains its own explicit fixture label.

## Updating an existing Streamlit deployment

Uploading these static files will **not** make Streamlit host this frontend. Use GitHub Pages for this build, keep the old Streamlit branch if useful, and update the portfolio/LinkedIn demo link only after the Pages deployment is verified. No existing Streamlit URL or repository state was available for validation here.
