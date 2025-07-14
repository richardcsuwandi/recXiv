# RecXiv Vercel Deployment Guide

This guide explains how to deploy RecXiv to Vercel with Git LFS support for large files.

## Prerequisites

1. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
2. **Git LFS**: Already configured in this repository
3. **GitHub Repository**: Push your code to GitHub with LFS files

## Step 1: Prepare Your Repository

### Git LFS Setup (Already Done)
```bash
# The following has already been configured:
git lfs install
git lfs track "*.gpu"
git lfs track "data/*/metadata.json"
git lfs track "*.pkl"
```

### Push to GitHub
```bash
git add .
git commit -m "Add Vercel deployment configuration"
git push origin main
```

## Step 2: Deploy to Vercel

### Option A: Vercel CLI (Recommended)
```bash
# Install Vercel CLI
npm i -g vercel

# Login to Vercel
vercel login

# Deploy
vercel --prod
```

### Option B: GitHub Integration
1. Go to [vercel.com/dashboard](https://vercel.com/dashboard)
2. Click "New Project"
3. Import your GitHub repository
4. Vercel will automatically detect the configuration

## Step 3: Configuration Notes

### Requirements
- Uses `requirements-vercel.txt` for CPU-optimized dependencies
- Switches from `faiss-gpu` to `faiss-cpu` for serverless compatibility
- Uses CPU-only PyTorch versions to reduce bundle size

### Vercel Settings
- **Function Timeout**: 30 seconds (configured in `vercel.json`)
- **Max Lambda Size**: 50MB
- **Runtime**: Python 3.9+

### Environment Variables
Set these in Vercel dashboard if needed:
- `PYTHONPATH`: `/var/task` (already configured)

## Step 4: Optimization Tips

### Cold Start Optimization
1. **Model Caching**: Sentence transformers models are cached automatically
2. **Faiss Index**: Pre-loaded on function initialization
3. **Memory Usage**: Monitor function memory consumption

### Performance Considerations
- First request may take 10-20 seconds (cold start)
- Subsequent requests should be fast (< 2 seconds)
- Consider using Vercel Pro for better performance

## Step 5: Monitoring and Debugging

### Vercel Dashboard
- Monitor function execution time
- Check error logs
- View deployment status

### Local Testing
```bash
# Test locally with Vercel dev
vercel dev

# Or use Flask directly
cd app
python app.py
```

## Troubleshooting

### Common Issues
1. **Large File Errors**: Ensure Git LFS is properly configured
2. **Import Errors**: Check `requirements-vercel.txt` dependencies
3. **Timeout Issues**: Reduce model size or increase timeout

### File Size Limits
- Function size limit: 50MB (compressed)
- Git LFS files are downloaded during build
- Consider using smaller models if deployment fails

### Memory Issues
- Vercel functions have memory limits
- Monitor usage in dashboard
- Consider model quantization if needed

## Production Considerations

### Domain Setup
- Configure custom domain in Vercel dashboard
- Set up SSL (automatic with Vercel)

### Caching
- Static files are automatically cached
- Consider adding cache headers for API responses

### Scaling
- Vercel automatically scales functions
- Monitor usage and costs
- Consider Edge Functions for better global performance

## Support

For issues:
1. Check Vercel deployment logs
2. Verify Git LFS files are accessible
3. Test locally with `vercel dev`
4. Check Vercel community forums 