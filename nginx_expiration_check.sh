#!/bin/bash

# * Vhost config file path
vhost_config_path="/etc/nginx/conf.d"

# * Aliyun SMS script path
sms_script_path="/home/workspace/aliyun_sms/send_sms.py"

# * Python virtualenv path(optional)
python_virtualenv_path="/home/workspace/aliyun_sms/.aliyun_sms/bin/activate"

# * Log file path
log_file_path="/home/workspace/aliyun_sms/nginx_expiration_check.log"

# * Get current date in YYYY-MM-DD format
current_date=$(date +%Y-%m-%d)

# * Source Python virtualenv
source "$python_virtualenv_path"

# * For loop to iterate through all vhost config files in the vhost config path
for vhost_config_file in $(ls "$vhost_config_path"/*.conf); do
    # * Pick out the vhost name from the vhost config file name
    vhost_name=$(basename "$vhost_config_file" .conf)

    # * GET phone_number list
    phone_numbers=()
    # while IFS= read -r vhost_config_file; do
        while IFS= read -r line; do
            if [[ $line == *"# phone_number="* ]]; then
                phone_number=$(echo "$line" | sed -n 's/.*phone_number=\(.*\)/\1/p')
                phone_numbers+=("$phone_number")
                echo "Found phone number: $phone_number"
            fi
        done < "$vhost_config_file"
    done < <(find "$vhost_config_path" -name "*.conf")

    # * Get phone number from vhost config file(only one phone number)
    # phone_number=$(grep "phone_number=" "$vhost_config_file" | cut -d'=' -f2)
    # echo "Found phone number: $phone_number"

    # * Get expiration date from vhost config file
    expiration_date=$(grep "expiration_date=" "$vhost_config_file" | cut -d'=' -f2)
    days_remaining=$(( ($(date -d "$expiration_date" +%s) - $(date -d "$current_date" +%s)) / 86400 ))

    # * Send SMS if expiration date is 30, 15 or 7 days away
    if [[ $days_remaining -eq 30 || $days_remaining -eq 15 || $days_remaining -eq 7 ]]; then
        message="Your virtual host $vhost_name will expire in $days_remaining days."
        for phone_number in "${phone_numbers[@]}"; do
            python "$sms_script_path" "$phone_number" "$vhost_name" "$days_remaining"
        done
        # python "$sms_script_path" "$phone_number" "$vhost_name" “$days_remaining”
        echo "$(date +%Y-%m-%d) - Vhost: $vhost_name, Days Remaining: $days_remaining" >> "$log_file_path"
    fi

    # * Disable vhost if expiration date is 0 days away, just comment out the listen directives
    if [[ $current_date > $expiration_date ]]; then
        sed -i 's/listen 80;/#listen 80;/g' "$vhost_config_file"
        sed -i 's/listen 443 ssl;/#listen 443 ssl;/g' "$vhost_config_file"
        nginx -s reload
    fi