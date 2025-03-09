#\!/bin/bash

# Ask the user for their public IP or domain
echo "Enter your public IP address or domain name (without http:// or port):"
read domain

# Replace placeholder in .env file
sed -i'.bak' "s/your-public-ip-or-domain/$domain/g" .env

# Display the changes
echo "Updated .env file with domain: $domain"
echo "Please verify these changes are correct:"
grep "EXTERNAL_DOMAIN\|SERVER_NAME" .env

echo -e "\nTo apply these changes, run: docker-compose up -d"
