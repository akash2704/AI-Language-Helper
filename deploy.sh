#!/bin/bash

# AI Language Helper Deployment Script

echo "🚀 Starting deployment of AI Language Helper..."

# Check if required environment variables are set
if [ -z "$SECRET_KEY" ] || [ -z "$GEMINI_API_KEY" ]; then
    echo "❌ Error: Please set SECRET_KEY and GEMINI_API_KEY environment variables"
    exit 1
fi

# Deploy Backend
echo "📦 Deploying backend to AWS Lambda..."
cd Backend
npm install
serverless deploy --stage prod
if [ $? -eq 0 ]; then
    echo "✅ Backend deployed successfully!"
else
    echo "❌ Backend deployment failed!"
    exit 1
fi

# Get API Gateway URL
API_URL=$(serverless info --stage prod | grep "ServiceEndpoint" | awk '{print $2}')
echo "🔗 API Gateway URL: $API_URL"

# Deploy Frontend
echo "🌐 Deploying frontend to Vercel..."
cd ../language-learning-frontend
export NEXT_PUBLIC_API_URL=$API_URL
npm run build

echo "✅ Deployment completed!"
echo "🔗 Backend API: $API_URL"
echo "📝 Don't forget to update your frontend environment variables with the API URL"
