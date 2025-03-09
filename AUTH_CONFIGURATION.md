# Authentication Service Configuration Guide

This guide will help you set up the authentication service for your Telegram AI Assistant.

## Overview

The authentication service allows your Telegram bot to authenticate users via Google OAuth, ensuring that only users with @smu.edu.sg email addresses can access the bot.

## Prerequisites

1. A server with a public IP address (or domain name)
2. Google OAuth credentials (Client ID and Client Secret)
3. Docker and Docker Compose installed on your server

## Step 1: Create Google OAuth Credentials

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Navigate to "APIs & Services" > "Credentials"
4. Click "Create Credentials" and select "OAuth client ID"
5. Set the application type to "Web application"
6. Add your domain or IP to the "Authorized JavaScript origins" (e.g., `http://your-server-ip:5050`)
7. Add your callback URL to the "Authorized redirect URIs" (e.g., `http://your-server-ip:5050/callback`)
8. Click "Create" and note down your Client ID and Client Secret

## Step 2: Update Your Environment Variables

1. Copy the `.env.auth` file to `.env` (or add the variables to your existing `.env` file)
2. Update the following variables:
   - `GOOGLE_CLIENT_ID`: Your Google OAuth Client ID
   - `GOOGLE_CLIENT_SECRET`: Your Google OAuth Client Secret
   - `AUTH_SECRET_KEY`: A random string for session encryption (you can generate one with `python -c "import secrets; print(secrets.token_hex(32))"`)
   - `EXTERNAL_DOMAIN`: Your server's public IP or domain (e.g., `example.com:5050` or `123.456.789.101:5050`)
   - `SERVER_NAME`: Same as `EXTERNAL_DOMAIN`

Example:
```
GOOGLE_CLIENT_ID=123456789012-abcdefghijklmnopqrstuvwxyz123456.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-abcdefghijklmnopqrstuvwxyz12345
AUTH_SECRET_KEY=3b586bbcee39a7b04364341869a5132fbf3cb305f87cdbc6aa1fb053c1e395e8
EXTERNAL_DOMAIN=example.com:5050
SERVER_NAME=example.com:5050
```

## Step 3: Start the Services

1. Rebuild and start all services:
   ```
   docker-compose up --build -d
   ```

2. Check the logs to ensure everything is working:
   ```
   docker-compose logs auth-service
   ```

## Step 4: Test the Authentication

1. Add your bot to Telegram and start a conversation
2. Type `/login` to get the authentication link
3. Click the link and authenticate with your SMU email (@smu.edu.sg)
4. After successful authentication, you should be able to interact with the bot

## Troubleshooting

### Authentication Link Not Working

If the authentication link doesn't work, check the following:

1. Ensure your server is accessible from the internet on port 5050
2. Verify that the `EXTERNAL_DOMAIN` in your `.env` file matches your actual public IP or domain
3. Check if the Google OAuth credentials are correctly set up with the right redirect URI

### Users Can't Authenticate

If users can authenticate but still receive "Please authenticate" messages:

1. Check the auth-service logs for any errors:
   ```
   docker-compose logs auth-service
   ```
2. Ensure the bot can communicate with the auth-service:
   ```
   docker-compose logs bot | grep auth
   ```

### MongoDB Connection Issues

If MongoDB is not connecting:

1. Check the MongoDB logs:
   ```
   docker-compose logs mongo
   ```
2. Ensure the volume for MongoDB data is properly mounted

## Advanced Configuration

### Custom Ports

If you want to use a different port:

1. Update the port mapping in `docker-compose.yml`:
   ```yaml
   auth-service:
     ports:
       - "8080:5050"  # Maps external port 8080 to internal port 5050
   ```
2. Update `EXTERNAL_DOMAIN` and `SERVER_NAME` in `.env` to use the new port

### HTTPS Support

For production environments, it's recommended to use HTTPS:

1. Set up a reverse proxy (like Nginx) with SSL termination
2. Update `EXTERNAL_DOMAIN` and `SERVER_NAME` to use https:// protocol
3. Update your Google OAuth credentials to use HTTPS URLs