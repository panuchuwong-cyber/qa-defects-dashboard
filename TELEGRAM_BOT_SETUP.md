# Telegram Bot Setup for QA Dashboard

## Step 1: Create Bot (~2 minutes)

1. Open Telegram, search for **@BotFather**
2. Send: `/newbot`
3. BotFather asks for name: send `3K QA Dashboard Bot`
4. BotFather asks for username: send `threeK_qa_dashboard_bot` (must end in `_bot`)
5. BotFather gives you a **token** like:
   ```
   1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
   ```
6. **Save this token** — Kanom needs it

## Step 2: Get Chat IDs

For each person who should receive sync messages:

1. Open chat with your new bot (search `threeK_qa_dashboard_bot`)
2. Send any message (e.g., "hello")
3. Open this URL in browser (replace TOKEN):
   ```
   https://api.telegram.org/bot<TOKEN>/getUpdates
   ```
4. Find your chat ID in the JSON response:
   ```json
   {
     "chat": {"id": 1524914087, "first_name": "Nu"},
     "text": "hello"
   }
   ```
5. The number `1524914087` is your **chat_id**

## Step 3: Add to Streamlit Secrets

Kanom will add these to `.streamlit/secrets.toml`:

```toml
telegram_bot_token = "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"
telegram_chat_id = "1524914087"  # Nu (primary)
telegram_kanom_chat_id = "9876543210"  # Kanom (auto-sync target)
```

## Step 4: Test

Click "📤 SYNC TO KANOM" button in dashboard. If setup is correct, message arrives in Telegram within 1 second.
