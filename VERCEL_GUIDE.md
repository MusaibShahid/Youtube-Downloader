# 🚀 How to Upload to Vercel

Since your project is already on GitHub, uploading to Vercel is simple and can be done in a few clicks.

## 📦 Step-by-Step Deployment

1. **Sign up / Login to Vercel**
   - Go to [vercel.com](https://vercel.com) and sign in with your GitHub account.

2. **Import Project**
   - Click on **"Add New"** > **"Project"**.
   - Find your **`Youtube-Downloader`** repository and click **"Import"**.

3. **Configure Settings**
   - **Framework Preset**: Other (it should detect Python automatically).
   - **Root Directory**: `./` (default).
   - **Environment Variables**: You don't *need* any, but if you want to force server mode, you can add:
     - `YT_SERVER_MODE` = `true`

4. **Deploy**
   - Click **"Deploy"**. Vercel will build your app and give you a live URL!

---

## ⚠️ Important Limitations on Vercel

Vercel is a **Serverless** platform, which means it has some differences compared to running on your own computer:

*   **FFmpeg Compatibility**: High-quality (4K/8K) downloads require merging video and audio, which uses FFmpeg. Vercel doesn't have FFmpeg pre-installed. 
    - *Result*: You may only be able to download "Progressive" streams (up to 720p) successfully.
*   **Timeouts**: Vercel functions have a limit (usually 10 to 60 seconds). Large video downloads might take longer than this and could be cut off.
*   **Temporary Storage**: Files are saved to `/tmp`, which is temporary. They will disappear after the download session is over (this is actually good for privacy!).

## 💡 Recommendation
If you find that Vercel is too slow or fails on large videos, I recommend:
1. **Render.com** or **Railway.app** (Better for Python apps with long-running tasks).
2. **Personal Server**: Running on your own machine using `start_server.bat` is the most reliable way for 4K/8K downloads.
