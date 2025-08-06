# ⚡ Groq Integration Setup Guide

## 🎯 **Migration Complete: OpenAI → Groq**

Your mental health chatbot has been successfully migrated from OpenAI to Groq! This provides you with:

- **Lightning-fast responses** (often under 1 second!)
- **High-quality Llama models** for natural conversations
- **Generous free tier** with high rate limits
- **Cost-effective API usage** for production
- **Excellent performance** for mental health support

## 🔑 **Getting Your Groq API Key**

### **Step 1: Create Groq Account**
1. Go to **Groq Console**: https://console.groq.com/
2. **Sign up** or **log in** with your account
3. Complete account verification if required

### **Step 2: Generate API Key**
1. Navigate to **API Keys** section
2. Click **"Create API Key"**
3. Give it a name (e.g., "Mental Health Chatbot")
4. **Copy the API key** (save it securely!)

### **Step 3: Configure Your Environment**
1. Open the `.env` file in your project
2. Replace `your_groq_api_key_here` with your actual API key:
   ```
   GROQ_API_KEY=gsk_your-actual-groq-api-key-here
   ```
3. Save the file

## 🛠️ **Installation & Setup**

### **Install Dependencies**
```bash
cd "Personalized_Mental_Healthcare-Chatbot-main"
pip install -r requirements.txt
```

### **Run the Application**
```bash
streamlit run Personalized_Mental_Healthcare-Chatbot.py
```

## 🧠 **New Features with Grok**

### **Enhanced AI Responses**
- **More empathetic** and natural conversations
- **Better understanding** of mental health contexts
- **Improved crisis detection** and response
- **Contextual awareness** from knowledge base

### **Smart Fallback System**
1. **Knowledge Base First**: Uses 97 mental health Q&As
2. **Grok AI Second**: For complex or unique queries
3. **Graceful Degradation**: Falls back to knowledge base if API fails

### **Better Error Handling**
- Clear error messages for API issues
- Automatic fallback to knowledge base
- User-friendly troubleshooting guides

## 💰 **Cost Benefits**

### **Grok vs OpenAI Pricing**
- **More competitive rates** for API usage
- **Better value** for conversational AI
- **Transparent pricing** structure

### **Usage Optimization**
- Knowledge base reduces API calls
- Efficient token usage
- Smart caching of responses

## 🧪 **Testing Your Setup**

### **Quick Test Questions**
Try these to test your Grok integration:

1. **Simple greeting**: "Hello, how are you?"
2. **Mental health query**: "I'm feeling anxious about work"
3. **Knowledge base test**: "What is depression?"
4. **Crisis scenario**: "I'm having thoughts of self-harm"

### **Expected Behavior**
- ✅ **Knowledge base questions** get instant responses
- ✅ **Complex queries** use Grok AI
- ✅ **API errors** fall back gracefully
- ✅ **Crisis detection** provides resources

## 🔧 **Troubleshooting**

### **Common Issues**

**❌ "API Authentication Error"**
- Check your API key in `.env` file
- Verify the key is valid at https://console.x.ai/
- Ensure no extra spaces in the key

**❌ "Rate Limit Exceeded"**
- Wait a moment and try again
- Check your xAI account usage limits
- Consider upgrading your plan if needed

**❌ "API Endpoint Error"**
- Verify internet connection
- Check if xAI services are operational
- The app will use knowledge base as fallback

### **Fallback Mode**
If Grok API is unavailable, the chatbot will:
- Use the 97-entry mental health knowledge base
- Provide crisis resources and support
- Show clear status messages
- Continue functioning for basic support

## 🎯 **Next Steps**

### **Immediate Actions**
1. ✅ Get your Grok API key from https://console.x.ai/
2. ✅ Update the `.env` file with your key
3. ✅ Test the application with sample questions
4. ✅ Verify both text and voice input work

### **Optional Enhancements**
- **Voice Integration**: Test the voice input feature
- **Knowledge Base**: Add more mental health Q&As
- **Customization**: Modify prompts for your specific needs
- **Monitoring**: Set up usage tracking

## 📊 **System Status Check**

When you run the app, check the sidebar for:
- ✅ **Knowledge Base**: Should show "97 entries"
- ✅ **Grok API**: Should show "Configured"
- ✅ **Voice Input**: May require PyAudio setup

## 🆘 **Support Resources**

### **Technical Support**
- **xAI Documentation**: https://docs.x.ai/
- **API Status**: Check xAI status page
- **Community**: xAI developer forums

### **Mental Health Resources**
- **Crisis Hotline**: 988 (US)
- **Crisis Text**: Text HOME to 741741
- **Emergency**: 911

## 🎉 **Congratulations!**

Your mental health chatbot is now powered by Grok's advanced AI capabilities! The migration provides:

- **Better user experience** with more natural conversations
- **Reliable fallback system** using knowledge base
- **Cost-effective operation** with competitive pricing
- **Future-ready platform** with xAI's latest technology

**Your mental health support tool is now more powerful and reliable than ever!** 🧠💙
