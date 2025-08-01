# LLM Configuration Guide

## Overview

MindGen supports multiple LLM providers, each with their own API keys and configuration options. This guide explains how to set up and configure each provider.

## Supported LLM Providers

### 1. Qwen (via Alibaba Cloud)

**What is QWEN_API_KEY?**
- `QWEN_API_KEY` is the API key for Alibaba Cloud DashScope, which provides access to Qwen models
- It's used to access Qwen models through Alibaba Cloud's infrastructure
- You only need one API key for authentication

**Configuration:**
```yaml
# config/models.yaml
models:
  qwen:
    api_url: "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
    api_key: "${QWEN_API_KEY}"
    model_name: "qwen-plus"
    max_tokens: 16000
    temperature: 0.7
    timeout: 45
```

**Environment Variables:**
```bash
# .env
QWEN_API_KEY=your-qwen-api-key-here
```

**How to get API keys:**
1. Visit [Alibaba Cloud Bailian Console](https://bailian.console.aliyun.com/)
2. Create an account and get your API key
3. Add it to your `.env` file

**Token Limits:**
- Default max_tokens: 16,000 (suitable for detailed teaching plans)
- Context window: Up to 32K tokens
- Optimized for Chinese language content

### 2. DeepSeek

**Configuration:**
```yaml
# config/models.yaml
models:
  deepseek:
    api_url: "https://api.deepseek.com/v1/chat/completions"
    api_key: "${DEEPSEEK_API_KEY}"
    model_name: "deepseek-reasoner"
    max_tokens: 32000
    temperature: 0.7
    timeout: 30
```

**Environment Variables:**
```bash
# .env
DEEPSEEK_API_KEY=your-deepseek-api-key-here
```

**How to get API keys:**
1. Visit [DeepSeek API Console](https://platform.deepseek.com/)
2. Create an account and get your API key
3. Add it to your `.env` file

**Available Models:**
- `deepseek-reasoner` - DeepSeek-R1-0528 (reasoning model, 128K context)
- `deepseek-chat` - DeepSeek-V3-0324 (chat model, 128K context)

**Token Limits:**
- Default max_tokens: 32,000 (suitable for multi-round teaching plan generation)
- Context window: Up to 128K tokens
- Recommended for complex educational content generation

### 3. Personal ChatGPT Server (Primary - for China users)

**Configuration:**
```yaml
# config/models.yaml
models:
  personal_chatgpt:
    api_url: "${PERSONAL_CHATGPT_URL}"
    api_key: "${PERSONAL_CHATGPT_API_KEY}"
    model_name: "gpt-4o"
    max_tokens: 32000
    temperature: 0.7
    timeout: 60
```

**Environment Variables:**
```bash
# .env
PERSONAL_CHATGPT_URL=your-personal-chatgpt-server-url-here
PERSONAL_CHATGPT_API_KEY=your-personal-chatgpt-api-key-here
```

**How to configure:**
1. Set up your personal ChatGPT server (e.g., using [OpenWebUI](https://openwebui.com/) or similar)
2. Get the server URL and API key
3. Add them to your `.env` file
4. The server should be OpenAI-compatible

**Token Limits:**
- Default max_tokens: 32,000 (suitable for comprehensive educational content)
- Context window: Up to 128K tokens
- Excellent for complex multi-step reasoning tasks
- **Priority**: Primary configuration for China users

### 4. OpenAI GPT-4o (Removed - using Personal ChatGPT Server only)

**Note:** OpenAI GPT-4o configuration has been removed. The application now uses only the Personal ChatGPT Server for GPT-4o functionality.

## Configuration Options

Each LLM provider supports the following configuration options:

| Option | Description | Default |
|--------|-------------|---------|
| `api_url` | The API endpoint URL | Varies by provider |
| `api_key` | API key for authentication | Required |
| `model_name` | The specific model to use | Varies by provider |
| `max_tokens` | Maximum tokens in response | Varies by model |
| `temperature` | Creativity level (0.0-1.0) | 0.7 |
| `timeout` | Request timeout in seconds | Varies by provider |
| `retry_attempts` | Number of retry attempts | 3 |
| `retry_delay` | Delay between retries | Varies by provider |
| `rate_limit` | Requests per minute limit | 100 |

## Environment Variable Substitution

The configuration supports environment variable substitution using `${VARIABLE_NAME}` syntax:

```yaml
models:
  qwen:
    api_key: "${QWEN_API_KEY}"  # Will be replaced with actual value
  personal_chatgpt:
    api_url: "${PERSONAL_CHATGPT_URL}"  # Will be replaced with actual value
    api_key: "${PERSONAL_CHATGPT_API_KEY}"
```

## Adding New LLM Providers

To add a new LLM provider:

1. **Add configuration to `config/models.yaml`:**
```yaml
models:
  new_provider:
    api_url: "https://api.newprovider.com/v1/chat/completions"
    api_key: "${NEW_PROVIDER_API_KEY}"
    model_name: "new-model"
    max_tokens: 4000
    temperature: 0.7
    timeout: 30
```

2. **Add environment variable to `env.example`:**
```bash
# New Provider API Configuration
NEW_PROVIDER_API_KEY=your-new-provider-api-key-here
```

3. **Update `services/llm_service.py` to initialize the new provider**

4. **Add the LangChain integration package to `requirements.txt`**

## Troubleshooting

### Common Issues

1. **"Failed to initialize LLM"**
   - Check that your API keys are correct
   - Verify the API keys are in your `.env` file
   - Ensure the LLM provider is available and your account is active

2. **"Timeout errors"**
   - Increase the `timeout` value in the configuration
   - Check your internet connection
   - Verify the API endpoint is accessible

3. **"Rate limit exceeded"**
   - Reduce the `rate_limit` value
   - Implement request throttling
   - Check your provider's rate limits

### Testing Configuration

You can test your LLM configuration by running:

```python
from services.llm_service import LangChainLLMService
from config.config_manager import ConfigManager

config_manager = ConfigManager()
llm_service = LangChainLLMService(config_manager)

# Test available models
available_models = llm_service.get_available_models()
print(f"Available models: {available_models}")

# Test a specific model
test_result = llm_service.test_model_connection('qwen')
print(f"Test result: {test_result}")
```

## Security Best Practices

1. **Never commit API keys to version control**
   - Use `.env` files for local development
   - Use environment variables in production
   - Add `.env` to `.gitignore`

2. **Rotate API keys regularly**
   - Set up key rotation schedules
   - Monitor API key usage

3. **Use least privilege**
   - Only grant necessary permissions
   - Monitor API usage for anomalies

4. **Secure your configuration**
   - Use strong, unique API keys
   - Store secrets securely in production
   - Use environment-specific configurations 