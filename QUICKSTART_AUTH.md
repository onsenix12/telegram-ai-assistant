# Authentication Quickstart Guide

## Step 1: Get Your Server's Public IP Address

Run this command on your server to get your public IP:

```bash
curl -s https://api.ipify.org
```

Remember this IP address. If you have a domain name pointing to your server, you can use that instead.

## Step 2: Create Google OAuth Credentials

1. Go to https://console.cloud.google.com/
2. Create a new project
3. Navigate to "APIs & Services" > "Credentials"
4. Click "Create Credentials" > "OAuth client ID"
5. Choose "Web application"
6. Add authorized JavaScript origins: `http://YOUR_PUBLIC_IP:5050`
7. Add authorized redirect URIs: `http://YOUR_PUBLIC_IP:5050/callback`
8. Click "Create" and copy your Client ID and Client Secret

## Step 3: Update Environment Variables

Edit your .env file (create it if it doesn't exist):

```bash
# Run this script to update the authentication configuration
./update_auth_domain.sh
```

When prompted, enter your public IP or domain name.

Then, edit the .env file to add your Google credentials:

```bash
# Add these lines to your .env file
GOOGLE_CLIENT_ID=your-client-id-here
GOOGLE_CLIENT_SECRET=your-client-secret-here
AUTH_SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
```

## Step 4: Start the Services

```bash
docker-compose up -d --build
```

## Step 5: Test the Authentication

1. Open Telegram and message your bot
2. Type `/login` to get an authentication link
3. Click the link and log in with your SMU email

## Common Issues

### Authentication link doesn't work

Make sure:
- Your server is accessible on port 5050 (check your firewall settings)
- Your EXTERNAL_DOMAIN in .env is correct
- Your Google OAuth credentials have the right redirect URI

### Users can't authenticate

Check:
- The auth-service logs: `docker-compose logs auth-service`
- MongoDB connectivity: `docker-compose logs mongo`
- Make sure you're using an @smu.edu.sg email

## More Information

For detailed configuration and troubleshooting, see [AUTH_CONFIGURATION.md](AUTH_CONFIGURATION.md)