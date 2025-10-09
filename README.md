# AI Language Helper - Serverless Edition

AI Language Helper is a serverless, AI-powered language learning platform built with AWS Lambda, DynamoDB, and Next.js. It provides interactive chat-based learning, real-time corrections, and personalized feedback to help users improve their language skills.

## 🚀 Features

- **AI-Powered Chat**: Practice conversations with an AI that provides instant corrections and suggestions
- **Serverless Architecture**: Built on AWS Lambda for scalability and cost-effectiveness
- **DynamoDB Storage**: Fast, reliable NoSQL database for user data and sessions
- **User Authentication**: Secure JWT-based authentication system
- **Personalized Feedback**: Track mistakes and receive targeted improvement suggestions
- **Multiple Languages & Levels**: Choose your target language and proficiency level
- **Modern UI**: Built with Next.js, React, and Tailwind CSS for a responsive experience

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Next.js       │    │   AWS Lambda     │    │   DynamoDB      │
│   Frontend      │───▶│   (Flask)       │───▶│   Tables        │
│   (Vercel)      │    │   + Gemini AI    │    │   - Users       │
└─────────────────┘    └──────────────────┘    │   - Sessions    │
                                               │   - Mistakes    │
                                               └─────────────────┘
```

## 📁 Project Structure

```
AI-language-helper/
├── Backend/                     # Serverless Python backend
│   ├── app.py                   # Main Flask application
│   ├── lambda_handler.py        # AWS Lambda handler
│   ├── db_utils.py             # DynamoDB utilities
│   ├── chatbot.py              # AI chat logic
│   ├── serverless.yml          # Serverless Framework config
│   ├── requirements.txt        # Python dependencies
│   └── .env.example           # Environment variables template
├── language-learning-frontend/  # Next.js frontend
│   ├── src/                    # React/Next.js source code
│   ├── package.json           # JS dependencies
│   ├── next.config.js         # Next.js configuration
│   └── .env.example          # Frontend environment template
├── .github/workflows/         # CI/CD workflows
│   └── deploy-backend.yml     # Backend deployment
├── deploy.sh                  # Local deployment script
└── README.md                  # This file
```

## 🛠️ Prerequisites

- **Node.js** 18+
- **Python** 3.9+
- **AWS CLI** configured with appropriate permissions
- **Serverless Framework** (`npm install -g serverless`)
- **Gemini API Key** from Google AI Studio
- **Vercel Account** (for frontend deployment)

## ⚙️ Setup & Deployment

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd AI-language-helper
```

### 2. Backend Setup

```bash
cd Backend

# Install Serverless plugins
npm init -y
npm install serverless-python-requirements

# Set environment variables
export SECRET_KEY="your-secret-key-here"
export GEMINI_API_KEY="your-gemini-api-key"

# Deploy to AWS
serverless deploy --stage prod
```

### 3. Frontend Setup

```bash
cd ../language-learning-frontend

# Install dependencies
npm install

# Set environment variables
export NEXT_PUBLIC_API_URL="https://your-api-gateway-url.amazonaws.com/prod"

# Build and deploy
npm run build
```

### 4. Automated Deployment

Use the provided deployment script:

```bash
# Set required environment variables
export SECRET_KEY="your-secret-key"
export GEMINI_API_KEY="your-gemini-api-key"

# Run deployment script
./deploy.sh
```

## 🔧 Environment Variables

### Backend (.env)
```bash
SECRET_KEY=your-jwt-secret-key
GEMINI_API_KEY=your-gemini-api-key
AWS_REGION=us-east-1
```

### Frontend (.env.local)
```bash
NEXT_PUBLIC_API_URL=https://your-api-gateway-url.amazonaws.com/prod
```

## 🚀 CI/CD Pipeline

The project includes GitHub Actions workflows for automated deployment:

### Required GitHub Secrets

**Backend Deployment:**
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `SECRET_KEY`
- `GEMINI_API_KEY`

### Deployment Triggers

- **Backend**: Pushes to `main` branch affecting `Backend/` directory or manual trigger

## 📊 AWS Resources Created

The serverless deployment creates:

- **Lambda Function**: Handles API requests
- **API Gateway**: REST API endpoint
- **DynamoDB Tables**:
  - `ai-language-helper-users-prod`
  - `ai-language-helper-sessions-prod`
  - `ai-language-helper-mistakes-prod`
- **IAM Roles**: Lambda execution role with DynamoDB permissions

## 🔒 Security Features

- JWT-based authentication
- Password hashing with Werkzeug
- CORS configuration
- Environment variable protection
- AWS IAM role-based access control

## 💰 Cost Optimization

- **Pay-per-request** DynamoDB billing
- **Lambda** charges only for execution time
- **API Gateway** charges per request
- **Vercel** free tier for frontend hosting

## 🧪 Local Development

### Backend
```bash
cd Backend
pip install -r requirements.txt
python app.py
```

### Frontend
```bash
cd language-learning-frontend
npm install
npm run dev
```

## 📝 API Endpoints

- `POST /register` - User registration
- `POST /login` - User authentication
- `GET /logout` - User logout
- `GET /api/verify_session` - Token verification
- `POST /api/start_session` - Start learning session
- `POST /api/chat` - Send chat message
- `GET /api/feedback` - Get learning feedback
- `GET /health` - Health check

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is for educational purposes. See individual files for license details.

## 🆘 Troubleshooting

### Common Issues

**Lambda Cold Starts**: First request may be slower due to cold start
**DynamoDB Throttling**: Increase read/write capacity if needed
**CORS Errors**: Ensure API Gateway CORS is properly configured

### Support

For issues and questions, please open a GitHub issue or contact the maintainer.

---

*Built with ❤️ by Akash Ajay Kallai using AWS Serverless Technologies.*
