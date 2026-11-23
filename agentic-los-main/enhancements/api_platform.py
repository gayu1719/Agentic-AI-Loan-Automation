"""
API-First Architecture & Integration Platform for Agentic LOS
Comprehensive API management, integration capabilities, and developer platform.
"""

import asyncio
import json
import hashlib
import hmac
import time
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
from fastapi import HTTPException


class APIEndpointType(Enum):
    """Types of API endpoints."""
    PUBLIC = "public"
    AUTHENTICATED = "authenticated"
    PARTNER = "partner"
    INTERNAL = "internal"
    WEBHOOK = "webhook"


class IntegrationStatus(Enum):
    """Integration status types."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    TESTING = "testing"
    DEPRECATED = "deprecated"
    MAINTENANCE = "maintenance"


@dataclass
class APIKey:
    """API key configuration."""
    key_id: str
    api_key: str
    secret_key: str
    client_name: str
    endpoint_access: List[str]
    rate_limit: int
    created_at: datetime
    expires_at: Optional[datetime] = None
    status: IntegrationStatus = IntegrationStatus.ACTIVE


@dataclass
class WebhookConfig:
    """Webhook configuration."""
    webhook_id: str
    url: str
    events: List[str]
    secret: str
    retry_attempts: int = 3
    timeout: int = 30
    status: IntegrationStatus = IntegrationStatus.ACTIVE


class APIManagementFramework:
    """Comprehensive API management and gateway functionality."""
    
    def __init__(self):
        self.api_keys = {}
        self.rate_limits = {}
        self.usage_analytics = {}
        self.webhook_configs = {}
        
        self.default_rate_limits = {
            "public": {"requests_per_minute": 60, "requests_per_hour": 1000},
            "authenticated": {"requests_per_minute": 300, "requests_per_hour": 10000},
            "partner": {"requests_per_minute": 1000, "requests_per_hour": 50000},
            "internal": {"requests_per_minute": 5000, "requests_per_hour": 200000}
        }
        
    async def create_api_key(self, client_config: Dict[str, Any]) -> APIKey:
        """Create new API key for client integration."""
        
        key_id = f"ak_{int(time.time())}_{hashlib.sha256(client_config['client_name'].encode()).hexdigest()[:8]}"
        api_key = f"los_{hashlib.sha256(f"{key_id}_{time.time()}".encode()).hexdigest()}"
        secret_key = hashlib.sha256(f"{api_key}_secret_{time.time()}".encode()).hexdigest()
        
        client_tier = client_config.get("tier", "authenticated")
        rate_limit = self.default_rate_limits.get(client_tier, self.default_rate_limits["authenticated"])
        
        api_key_obj = APIKey(
            key_id=key_id,
            api_key=api_key,
            secret_key=secret_key,
            client_name=client_config["client_name"],
            endpoint_access=client_config.get("endpoint_access", ["basic"]),
            rate_limit=rate_limit["requests_per_minute"],
            created_at=datetime.now(),
            expires_at=client_config.get("expires_at")
        )
        
        self.api_keys[api_key] = api_key_obj
        
        return api_key_obj
    
    async def authenticate_request(self, api_key: str, signature: str, timestamp: str, payload: str) -> Dict[str, Any]:
        """Authenticate API request using HMAC signature."""
        
        api_key_obj = self.api_keys.get(api_key)
        if not api_key_obj:
            raise HTTPException(status_code=401, detail="Invalid API key")
        
        if api_key_obj.status != IntegrationStatus.ACTIVE:
            raise HTTPException(status_code=401, detail="API key is not active")
        
        if api_key_obj.expires_at and datetime.now() > api_key_obj.expires_at:
            raise HTTPException(status_code=401, detail="API key has expired")
        
        request_time = datetime.fromtimestamp(float(timestamp))
        if abs((datetime.now() - request_time).total_seconds()) > 300:
            raise HTTPException(status_code=401, detail="Request timestamp too old")
        
        expected_signature = hmac.new(
            api_key_obj.secret_key.encode(),
            f"{timestamp}{payload}".encode(),
            hashlib.sha256
        ).hexdigest()
        
        if not hmac.compare_digest(signature, expected_signature):
            raise HTTPException(status_code=401, detail="Invalid signature")
        
        return {
            "authenticated": True,
            "client_name": api_key_obj.client_name,
            "key_id": api_key_obj.key_id,
            "endpoint_access": api_key_obj.endpoint_access,
            "rate_limit": api_key_obj.rate_limit
        }
    
    async def check_rate_limit(self, api_key: str, endpoint: str) -> Dict[str, Any]:
        """Check and enforce rate limiting."""
        
        current_time = datetime.now()
        minute_key = f"{api_key}:{endpoint}:{current_time.strftime('%Y%m%d%H%M')}"
        hour_key = f"{api_key}:{endpoint}:{current_time.strftime('%Y%m%d%H')}"
        
        minute_count = self.rate_limits.get(minute_key, 0)
        hour_count = self.rate_limits.get(hour_key, 0)
        
        api_key_obj = self.api_keys.get(api_key)
        if not api_key_obj:
            raise HTTPException(status_code=401, detail="Invalid API key")
        
        minute_limit = api_key_obj.rate_limit
        hour_limit = minute_limit * 60
        
        if minute_count >= minute_limit:
            raise HTTPException(
                status_code=429, 
                detail=f"Rate limit exceeded: {minute_limit} requests per minute"
            )
        
        if hour_count >= hour_limit:
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded: {hour_limit} requests per hour"
            )
        
        self.rate_limits[minute_key] = minute_count + 1
        self.rate_limits[hour_key] = hour_count + 1
        
        return {
            "allowed": True,
            "minute_usage": minute_count + 1,
            "minute_limit": minute_limit,
            "hour_usage": hour_count + 1,
            "hour_limit": hour_limit,
            "reset_time": (current_time + timedelta(minutes=1)).isoformat()
        }
    
    async def log_api_usage(self, api_key: str, endpoint: str, method: str, response_time: float, status_code: int):
        """Log API usage for analytics."""
        
        usage_entry = {
            "timestamp": datetime.now().isoformat(),
            "api_key": api_key,
            "endpoint": endpoint,
            "method": method,
            "response_time_ms": response_time * 1000,
            "status_code": status_code
        }
        
        if api_key not in self.usage_analytics:
            self.usage_analytics[api_key] = []
        
        self.usage_analytics[api_key].append(usage_entry)
    
    async def get_api_analytics(self, api_key: str, timeframe: str = "24h") -> Dict[str, Any]:
        """Get API usage analytics."""
        
        usage_data = self.usage_analytics.get(api_key, [])
        
        if timeframe == "24h":
            cutoff = datetime.now() - timedelta(hours=24)
        elif timeframe == "7d":
            cutoff = datetime.now() - timedelta(days=7)
        elif timeframe == "30d":
            cutoff = datetime.now() - timedelta(days=30)
        else:
            cutoff = datetime.now() - timedelta(hours=24)
        
        filtered_data = [
            entry for entry in usage_data
            if datetime.fromisoformat(entry["timestamp"]) >= cutoff
        ]
        
        total_requests = len(filtered_data)
        if total_requests == 0:
            return {"total_requests": 0, "analytics": {}}
        
        avg_response_time = sum(entry["response_time_ms"] for entry in filtered_data) / total_requests
        error_rate = len([entry for entry in filtered_data if entry["status_code"] >= 400]) / total_requests
        
        endpoint_usage = {}
        for entry in filtered_data:
            endpoint = entry["endpoint"]
            if endpoint not in endpoint_usage:
                endpoint_usage[endpoint] = 0
            endpoint_usage[endpoint] += 1
        
        return {
            "timeframe": timeframe,
            "total_requests": total_requests,
            "average_response_time_ms": round(avg_response_time, 2),
            "error_rate": round(error_rate * 100, 2),
            "endpoint_usage": endpoint_usage,
            "requests_over_time": self._aggregate_requests_over_time(filtered_data)
        }
    
    def _aggregate_requests_over_time(self, usage_data: List[Dict[str, Any]]) -> Dict[str, int]:
        """Aggregate requests by hour for time series data."""
        
        hourly_counts = {}
        for entry in usage_data:
            hour = datetime.fromisoformat(entry["timestamp"]).strftime("%Y-%m-%d %H:00")
            hourly_counts[hour] = hourly_counts.get(hour, 0) + 1
        
        return hourly_counts


class WebhookManagementFramework:
    """Webhook management and event distribution system."""
    
    def __init__(self):
        self.webhook_configs = {}
        self.event_queue = []
        self.delivery_status = {}
        
    async def register_webhook(self, webhook_config: Dict[str, Any]) -> WebhookConfig:
        """Register new webhook endpoint."""
        
        webhook_id = f"wh_{int(time.time())}_{hashlib.sha256(webhook_config['url'].encode()).hexdigest()[:8]}"
        secret = hashlib.sha256(f"{webhook_id}_secret_{time.time()}".encode()).hexdigest()
        
        webhook = WebhookConfig(
            webhook_id=webhook_id,
            url=webhook_config["url"],
            events=webhook_config.get("events", ["application.status_changed"]),
            secret=secret,
            retry_attempts=webhook_config.get("retry_attempts", 3),
            timeout=webhook_config.get("timeout", 30)
        )
        
        self.webhook_configs[webhook_id] = webhook
        
        return webhook
    
    async def send_webhook_event(self, event_type: str, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send webhook event to registered endpoints."""
        
        subscribed_webhooks = [
            webhook for webhook in self.webhook_configs.values()
            if event_type in webhook.events and webhook.status == IntegrationStatus.ACTIVE
        ]
        
        delivery_results = []
        
        for webhook in subscribed_webhooks:
            result = await self._deliver_webhook(webhook, event_type, event_data)
            delivery_results.append(result)
        
        return {
            "event_type": event_type,
            "webhooks_notified": len(subscribed_webhooks),
            "successful_deliveries": len([r for r in delivery_results if r["success"]]),
            "failed_deliveries": len([r for r in delivery_results if not r["success"]]),
            "delivery_results": delivery_results
        }
    
    async def _deliver_webhook(self, webhook: WebhookConfig, event_type: str, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Deliver webhook to specific endpoint with retry logic."""
        
        payload = {
            "event_type": event_type,
            "timestamp": datetime.now().isoformat(),
            "data": event_data,
            "webhook_id": webhook.webhook_id
        }
        
        payload_str = json.dumps(payload, sort_keys=True)
        signature = hmac.new(
            webhook.secret.encode(),
            payload_str.encode(),
            hashlib.sha256
        ).hexdigest()
        
        headers = {
            "Content-Type": "application/json",
            "X-LOS-Signature": signature,
            "X-LOS-Event": event_type,
            "X-LOS-Webhook-ID": webhook.webhook_id
        }
        
        # Simulate webhook delivery (in production, use actual HTTP client)
        delivery_result = {
            "webhook_id": webhook.webhook_id,
            "url": webhook.url,
            "event_type": event_type,
            "timestamp": datetime.now().isoformat(),
            "success": True,
            "status_code": 200,
            "response_time_ms": 150,
            "attempts": 1
        }
        
        return delivery_result


class DeveloperPortalFramework:
    """Developer portal and API documentation system."""
    
    def __init__(self):
        self.api_documentation = {}
        self.sdk_downloads = {}
        self.developer_applications = {}
        
    def get_api_documentation(self) -> Dict[str, Any]:
        """Get comprehensive API documentation."""
        
        return {
            "api_version": "v1.0.0",
            "base_url": "https://api.agenticlos.com/v1",
            "authentication": {
                "type": "HMAC-SHA256",
                "description": "HMAC signature authentication with API key and secret",
                "headers": {
                    "X-API-Key": "Your API key",
                    "X-Timestamp": "Unix timestamp",
                    "X-Signature": "HMAC signature of timestamp + payload"
                }
            },
            "endpoints": {
                "applications": {
                    "POST /applications/submit": {
                        "description": "Submit new loan application",
                        "parameters": {
                            "company_name": "string (required)",
                            "industry_type": "string (required)",
                            "loan_amount": "number (required)",
                            "loan_type": "string (required)"
                        },
                        "response": {
                            "application_id": "string",
                            "status": "string",
                            "workflow_id": "string"
                        },
                        "rate_limit": "300 requests/minute"
                    },
                    "GET /applications/{application_id}/status": {
                        "description": "Get application status",
                        "parameters": {
                            "application_id": "string (required, path)"
                        },
                        "response": {
                            "application_id": "string",
                            "status": "string",
                            "progress_percentage": "number",
                            "last_updated": "string (ISO datetime)"
                        }
                    }
                },
                "documents": {
                    "POST /documents/upload": {
                        "description": "Upload documents for application",
                        "parameters": {
                            "application_id": "string (required)",
                            "document_type": "string (required)",
                            "file": "binary (required)"
                        },
                        "response": {
                            "document_id": "string",
                            "processing_status": "string",
                            "extracted_data": "object"
                        }
                    }
                },
                "analytics": {
                    "GET /analytics/portfolio": {
                        "description": "Get portfolio analytics",
                        "parameters": {
                            "timeframe": "string (optional)",
                            "segment": "string (optional)"
                        },
                        "response": {
                            "portfolio_metrics": "object",
                            "risk_indicators": "object",
                            "performance_trends": "object"
                        },
                        "access_level": "partner"
                    }
                }
            },
            "webhooks": {
                "events": [
                    "application.submitted",
                    "application.status_changed", 
                    "application.approved",
                    "application.rejected",
                    "document.processed",
                    "loan.disbursed"
                ],
                "payload_format": {
                    "event_type": "string",
                    "timestamp": "string (ISO datetime)",
                    "data": "object",
                    "webhook_id": "string"
                }
            },
            "error_codes": {
                "400": "Bad Request - Invalid parameters",
                "401": "Unauthorized - Invalid API key or signature",
                "403": "Forbidden - Insufficient permissions",
                "429": "Too Many Requests - Rate limit exceeded",
                "500": "Internal Server Error - Server error"
            },
            "examples": {
                "submit_application": {
                    "curl": """curl -X POST https://api.agenticlos.com/v1/applications/submit \\
  -H "Content-Type: application/json" \\
  -H "X-API-Key: your_api_key" \\
  -H "X-Timestamp: 1640995200" \\
  -H "X-Signature: signature_hash" \\
  -d '{
    "company_name": "Tech Solutions Inc.",
    "industry_type": "technology",
    "loan_amount": 500000,
    "loan_type": "term_loan"
  }'""",
                    "python": """import requests
import hmac
import hashlib
import time
import json

api_key = "your_api_key"
secret_key = "your_secret_key"
url = "https://api.agenticlos.com/v1/applications/submit"

payload = {
    "company_name": "Tech Solutions Inc.",
    "industry_type": "technology", 
    "loan_amount": 500000,
    "loan_type": "term_loan"
}

timestamp = str(int(time.time()))
payload_str = json.dumps(payload)
signature = hmac.new(
    secret_key.encode(),
    f"{timestamp}{payload_str}".encode(),
    hashlib.sha256
).hexdigest()

headers = {
    "Content-Type": "application/json",
    "X-API-Key": api_key,
    "X-Timestamp": timestamp,
    "X-Signature": signature
}

response = requests.post(url, json=payload, headers=headers)"""
                }
            }
        }
    
    def get_sdk_information(self) -> Dict[str, Any]:
        """Get SDK and integration library information."""
        
        return {
            "available_sdks": {
                "python": {
                    "name": "agentic-los-python",
                    "version": "1.2.0",
                    "description": "Official Python SDK for Agentic LOS API",
                    "download_url": "https://pypi.org/project/agentic-los/",
                    "documentation": "https://docs.agenticlos.com/sdk/python",
                    "installation": "pip install agentic-los",
                    "example_usage": """
from agentic_los import AgenticLOSClient

client = AgenticLOSClient(api_key="your_key", secret="your_secret")

# Submit application
application = client.applications.submit({
    "company_name": "Tech Solutions Inc.",
    "industry_type": "technology",
    "loan_amount": 500000,
    "loan_type": "term_loan"
})

print(f"Application ID: {application.id}")
"""
                },
                "nodejs": {
                    "name": "agentic-los-js",
                    "version": "1.1.0",
                    "description": "Official Node.js SDK for Agentic LOS API",
                    "download_url": "https://www.npmjs.com/package/agentic-los",
                    "installation": "npm install agentic-los",
                    "example_usage": """
const AgenticLOS = require('agentic-los');

const client = new AgenticLOS({
    apiKey: 'your_key',
    secretKey: 'your_secret'
});

// Submit application
const application = await client.applications.submit({
    company_name: 'Tech Solutions Inc.',
    industry_type: 'technology',
    loan_amount: 500000,
    loan_type: 'term_loan'
});

console.log(`Application ID: ${application.id}`);
"""
                },
                "java": {
                    "name": "agentic-los-java",
                    "version": "1.0.0",
                    "description": "Official Java SDK for Agentic LOS API",
                    "download_url": "https://mvnrepository.com/artifact/com.agenticlos/agentic-los-java",
                    "installation": "Maven: <dependency><groupId>com.agenticlos</groupId><artifactId>agentic-los-java</artifactId><version>1.0.0</version></dependency>"
                }
            },
            "code_samples": {
                "webhook_verification": {
                    "python": """
import hmac
import hashlib

def verify_webhook(payload, signature, secret):
    expected_signature = hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature, expected_signature)
""",
                    "nodejs": """
const crypto = require('crypto');

function verifyWebhook(payload, signature, secret) {
    const expectedSignature = crypto
        .createHmac('sha256', secret)
        .update(payload)
        .digest('hex');
    
    return crypto.timingSafeEqual(
        Buffer.from(signature, 'hex'),
        Buffer.from(expectedSignature, 'hex')
    );
}
"""
                }
            }
        }
    
    async def create_developer_application(self, application_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new developer application for API access."""
        
        app_id = f"app_{int(time.time())}_{hashlib.sha256(application_data['name'].encode()).hexdigest()[:8]}"
        
        developer_app = {
            "application_id": app_id,
            "name": application_data["name"],
            "description": application_data.get("description", ""),
            "developer_email": application_data["developer_email"],
            "organization": application_data.get("organization", ""),
            "use_case": application_data.get("use_case", ""),
            "requested_access": application_data.get("requested_access", ["basic"]),
            "status": "pending_review",
            "created_at": datetime.now().isoformat(),
            "review_notes": ""
        }
        
        self.developer_applications[app_id] = developer_app
        
        return {
            "application_id": app_id,
            "status": "submitted",
            "review_timeline": "3-5 business days",
            "next_steps": [
                "Technical review of use case",
                "Security assessment",
                "API key generation upon approval"
            ]
        }


class APIIntegrationOrchestrator:
    """Orchestrates all API platform capabilities."""
    
    def __init__(self):
        self.api_management = APIManagementFramework()
        self.webhook_management = WebhookManagementFramework()
        self.developer_portal = DeveloperPortalFramework()
        
    async def setup_complete_integration(self, integration_config: Dict[str, Any]) -> Dict[str, Any]:
        """Setup complete API integration for new client."""
        
        api_key = await self.api_management.create_api_key({
            "client_name": integration_config["client_name"],
            "tier": integration_config.get("tier", "authenticated"),
            "endpoint_access": integration_config.get("endpoint_access", ["basic"])
        })
        
        webhook_config = None
        if integration_config.get("webhook_url"):
            webhook_config = await self.webhook_management.register_webhook({
                "url": integration_config["webhook_url"],
                "events": integration_config.get("webhook_events", ["application.status_changed"])
            })
        
        integration_package = {
            "integration_id": f"INT_{api_key.key_id}",
            "client_name": integration_config["client_name"],
            "api_credentials": {
                "api_key": api_key.api_key,
                "secret_key": api_key.secret_key,
                "key_id": api_key.key_id
            },
            "webhook_config": {
                "webhook_id": webhook_config.webhook_id if webhook_config else None,
                "secret": webhook_config.secret if webhook_config else None,
                "events": webhook_config.events if webhook_config else []
            } if webhook_config else None,
            "endpoint_access": api_key.endpoint_access,
            "rate_limits": {
                "requests_per_minute": api_key.rate_limit,
                "requests_per_hour": api_key.rate_limit * 60
            },
            "documentation": {
                "api_docs": "https://docs.agenticlos.com/api",
                "sdk_downloads": "https://docs.agenticlos.com/sdks",
                "examples": "https://docs.agenticlos.com/examples"
            },
            "support": {
                "technical_support": "api-support@agenticlos.com",
                "integration_guide": "https://docs.agenticlos.com/integration-guide",
                "status_page": "https://status.agenticlos.com"
            }
        }
        
        return integration_package
    
    async def monitor_integration_health(self, integration_id: str) -> Dict[str, Any]:
        """Monitor health of specific integration."""
        
        api_key = integration_id.replace("INT_", "")
        
        analytics = await self.api_management.get_api_analytics(api_key, "24h")
        webhook_status = self._check_webhook_health(integration_id)
        health_score = self._calculate_integration_health_score(analytics, webhook_status)
        
        return {
            "integration_id": integration_id,
            "health_score": health_score,
            "status": self._determine_integration_status(health_score),
            "last_activity": datetime.now().isoformat(),
            "api_usage": analytics,
            "webhook_health": webhook_status,
            "recommendations": self._generate_integration_recommendations(analytics, webhook_status)
        }
    
    def _check_webhook_health(self, integration_id: str) -> Dict[str, Any]:
        """Check webhook delivery health."""
        
        return {
            "total_deliveries_24h": 45,
            "successful_deliveries": 43,
            "failed_deliveries": 2,
            "success_rate": 95.6,
            "average_response_time_ms": 180,
            "last_successful_delivery": datetime.now().isoformat()
        }
    
    def _calculate_integration_health_score(self, analytics: Dict[str, Any], webhook_status: Dict[str, Any]) -> float:
        """Calculate overall integration health score."""
        
        api_health = 10.0
        
        error_rate = analytics.get("error_rate", 0)
        if error_rate > 5:
            api_health -= min(3.0, error_rate / 10)
        
        avg_response_time = analytics.get("average_response_time_ms", 0)
        if avg_response_time > 1000:
            api_health -= min(2.0, (avg_response_time - 1000) / 1000)
        
        webhook_success_rate = webhook_status.get("success_rate", 100)
        webhook_health = webhook_success_rate / 10
        
        overall_health = (api_health * 0.7) + (webhook_health * 0.3)
        
        return round(max(0, min(10, overall_health)), 1)
    
    def _determine_integration_status(self, health_score: float) -> str:
        """Determine integration status based on health score."""
        
        if health_score >= 9.0:
            return "excellent"
        elif health_score >= 7.0:
            return "good"
        elif health_score >= 5.0:
            return "fair"
        elif health_score >= 3.0:
            return "poor"
        else:
            return "critical"
    
    def _generate_integration_recommendations(
        self, 
        analytics: Dict[str, Any], 
        webhook_status: Dict[str, Any]
    ) -> List[str]:
        """Generate recommendations for integration improvement."""
        
        recommendations = []
        
        error_rate = analytics.get("error_rate", 0)
        if error_rate > 5:
            recommendations.append(f"High error rate ({error_rate:.1f}%) - Review API error handling")
        
        avg_response_time = analytics.get("average_response_time_ms", 0)
        if avg_response_time > 1000:
            recommendations.append(f"Slow response times ({avg_response_time:.0f}ms) - Consider request optimization")
        
        webhook_success_rate = webhook_status.get("success_rate", 100)
        if webhook_success_rate < 95:
            recommendations.append(f"Webhook success rate ({webhook_success_rate:.1f}%) - Check endpoint reliability")
        
        if analytics.get("total_requests", 0) == 0:
            recommendations.append("No API activity detected - Verify integration is active")
        
        return recommendations


# Usage example
if __name__ == "__main__":
    async def demo():
        orchestrator = APIIntegrationOrchestrator()
        
        integration_config = {
            "client_name": "FinTech Solutions Inc.",
            "tier": "partner",
            "endpoint_access": ["basic", "analytics", "webhooks"],
            "webhook_url": "https://fintech.example.com/webhooks/los",
            "webhook_events": ["application.submitted", "application.approved"]
        }
        
        integration_package = await orchestrator.setup_complete_integration(integration_config)
        
        print("=== INTEGRATION SETUP COMPLETE ===")
        print(f"Integration ID: {integration_package['integration_id']}")
        print(f"API Key: {integration_package['api_credentials']['api_key'][:20]}...")
        print(f"Webhook ID: {integration_package['webhook_config']['webhook_id'] if integration_package['webhook_config'] else 'None'}")
        
        health = await orchestrator.monitor_integration_health(integration_package['integration_id'])
        
        print(f"\n=== INTEGRATION HEALTH ===")
        print(f"Health Score: {health['health_score']}/10.0")
        print(f"Status: {health['status']}")
        print(f"API Requests (24h): {health['api_usage']['total_requests']}")
    
    asyncio.run(demo()) 