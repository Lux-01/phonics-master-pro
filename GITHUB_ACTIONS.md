# GitHub Actions - Automatic APK Build

This repository includes a GitHub Actions workflow that automatically builds the APK whenever you push code.

## How It Works

1. **Push code to GitHub** → Workflow triggers automatically
2. **GitHub builds the APK** using Flutter 3.19 + Android SDK
3. **Download the APK** from the Actions tab or release

## Setup

### 1. Push this repo to GitHub

If you haven't already:

```bash
cd phonics_app
git init
git add .
git commit -m "Initial commit - PhonicsMaster Pro"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/phonics-master-pro.git
git push -u origin main
```

### 2. Trigger a Build

**Option A: Push trigger (automatic)**
- Push any change to `main` or `master` branch
- Build starts automatically

**Option B: Manual trigger**
1. Go to your repo on GitHub
2. Click **Actions** tab
3. Select **Build APK** workflow
4. Click **Run workflow** → **Run workflow**

### 3. Download the APK

**From Actions:**
1. Go to **Actions** tab
2. Click on the completed workflow run
3. Scroll to **Artifacts** section
4. Download `PhonicsMaster-Pro-APK`

**From Release (if you create a tag):**
```bash
git tag v1.0.0
git push origin v1.0.0
```
- The APK will be attached to the release automatically

## Build Time

- First build: ~5-7 minutes (downloads Flutter, sets up SDK)
- Subsequent builds: ~3-5 minutes

## Troubleshooting

**Build fails:** Check the Actions log for error details

**Dependency issues:** Update `pubspec.yaml` and push again

**Code generation fails:** The workflow runs `build_runner` automatically

## Workflow Features

✅ Flutter 3.19 (stable)  
✅ JDK 17 (Temurin)  
✅ Automatic code generation  
✅ Release APK optimized  
✅ Artifact upload  
✅ Automatic release attachment (when tagged)

---

No local installation needed - GitHub does all the building!
