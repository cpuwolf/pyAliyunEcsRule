# Alibaba Cloud ECS Security Group Rule Auto-Update Tool

Automatically retrieves your current public IP address and updates it as the source address in Alibaba Cloud ECS security group rules.

## Features

- Automatically retrieves current public IP address
- Updates Alibaba Cloud ECS security group rules
- Supports deleting old rules and adding new rules

## Installation

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Configure Environment Variables

Set the following environment variables:

**Linux/macOS:**
```bash
export ALIBABA_CLOUD_ACCESS_KEY_ID=your_access_key_id
export ALIBABA_CLOUD_ACCESS_KEY_SECRET=your_access_key_secret
```

**Windows:**
```cmd
set ALIBABA_CLOUD_ACCESS_KEY_ID=your_access_key_id
set ALIBABA_CLOUD_ACCESS_KEY_SECRET=your_access_key_secret
```

## Usage

### Basic Usage

```bash
python update_security_group.py \
    --region-id cn-hangzhou \
    --security-group-id sg-xxxxxxxxxxxxx \
    --port-range 22/22
```

### Parameters

- `--region-id` (required): Alibaba Cloud region ID, e.g., `cn-hangzhou`
- `--security-group-id` (required): Security group ID
- `--port-range` (required): Port range, e.g., `22/22`, `80/80`, `443/443`
- `--ip-protocol` (optional): IP protocol, default: `tcp`
- `--description` (optional): Rule description, default: `Auto-updated from home IP`
- `--endpoint` (optional): Endpoint address (auto-generated if not specified)

## Docker Usage

### Build and Run

```bash
# Build image
docker build -t pyaliyun-ecs-rule .

# Run container
docker run --rm \
  -e ALIBABA_CLOUD_ACCESS_KEY_ID=your_access_key_id \
  -e ALIBABA_CLOUD_ACCESS_KEY_SECRET=your_access_key_secret \
  pyaliyun-ecs-rule \
  --region-id cn-hangzhou \
  --security-group-id sg-xxxxxxxxxxxxx \
  --port-range 22/22
```

## How It Works

1. Retrieves your current public IP address
2. Queries existing matching rules in the security group
3. Deletes old matching rules
4. Adds a new rule with the current IP address

## Important Notes

- Ensure your AccessKey has permission to modify security group rules
- Recommended: Use RAM user with `AliyunECSFullAccess` or custom policy including `ecs:AuthorizeSecurityGroup` and `ecs:RevokeSecurityGroup`
- IP addresses are automatically formatted as CIDR (e.g., `1.2.3.4/32`)

## License

GNU General Public License v3.0
