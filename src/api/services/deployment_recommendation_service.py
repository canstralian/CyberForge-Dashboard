"""
Deployment Recommendation Service

This module provides services for generating and managing deployment recommendations
based on threat intelligence, usage patterns, and cost optimization.
"""
import logging
import json
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import asyncio
from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
import pandas as pd
import numpy as np

from src.models.deployment import (
    DeploymentRecommendation, DeploymentSecurityConfig, DeploymentHistory,
    SecurityConfigLevel, DeploymentTimingRecommendation, DeploymentPlatform,
    DeploymentRegion, SecurityConfigCategory
)
from src.models.threat import Threat, ThreatSeverity, ThreatCategory
from src.models.indicator import Indicator
from src.models.subscription import SubscriptionTier, UserSubscription, SubscriptionPlan

logger = logging.getLogger(__name__)

class DeploymentRecommendationService:
    """Service for generating and managing deployment recommendations."""
    
    def __init__(self, session: AsyncSession):
        """Initialize the service with a database session."""
        self.session = session
    
    async def create_recommendation(
        self, 
        user_id: int,
        title: str,
        description: str,
        security_level: SecurityConfigLevel,
        timing_recommendation: DeploymentTimingRecommendation,
        timing_justification: str,
        recommended_window_start: Optional[datetime] = None,
        recommended_window_end: Optional[datetime] = None,
        estimated_cost: Optional[float] = None,
        cost_saving_potential: Optional[float] = None,
        cost_justification: Optional[str] = None,
        recommended_platform: Optional[DeploymentPlatform] = None,
        recommended_region: Optional[DeploymentRegion] = None,
        threat_assessment_summary: Optional[str] = None,
        security_settings: Optional[Dict[str, Any]] = None,
        high_risk_threats_count: int = 0,
        medium_risk_threats_count: int = 0,
        low_risk_threats_count: int = 0,
        expires_at: Optional[datetime] = None,
    ) -> DeploymentRecommendation:
        """
        Create a new deployment recommendation.
        
        Args:
            user_id: ID of the user this recommendation is for
            title: Title of the recommendation
            description: Detailed description of the recommendation
            security_level: Recommended security configuration level
            timing_recommendation: Recommendation for deployment timing
            timing_justification: Justification for the timing recommendation
            recommended_window_start: Start of recommended deployment window
            recommended_window_end: End of recommended deployment window
            estimated_cost: Estimated cost of deployment
            cost_saving_potential: Potential cost savings
            cost_justification: Justification for cost estimates
            recommended_platform: Recommended deployment platform
            recommended_region: Recommended deployment region
            threat_assessment_summary: Summary of threat assessment
            security_settings: Dict of security settings
            high_risk_threats_count: Count of high risk threats
            medium_risk_threats_count: Count of medium risk threats
            low_risk_threats_count: Count of low risk threats
            expires_at: When this recommendation expires
            
        Returns:
            The created DeploymentRecommendation object
        """
        security_settings_json = json.dumps(security_settings) if security_settings else None
        
        recommendation = DeploymentRecommendation(
            user_id=user_id,
            title=title,
            description=description,
            security_level=security_level,
            security_settings=security_settings_json,
            timing_recommendation=timing_recommendation,
            timing_justification=timing_justification,
            recommended_window_start=recommended_window_start,
            recommended_window_end=recommended_window_end,
            estimated_cost=estimated_cost,
            cost_saving_potential=cost_saving_potential,
            cost_justification=cost_justification,
            recommended_platform=recommended_platform,
            recommended_region=recommended_region,
            threat_assessment_summary=threat_assessment_summary,
            high_risk_threats_count=high_risk_threats_count,
            medium_risk_threats_count=medium_risk_threats_count,
            low_risk_threats_count=low_risk_threats_count,
            expires_at=expires_at
        )
        
        self.session.add(recommendation)
        await self.session.commit()
        await self.session.refresh(recommendation)
        
        return recommendation
    
    async def add_security_config(
        self,
        recommendation_id: int,
        category: SecurityConfigCategory,
        name: str,
        description: str,
        configuration_value: Dict[str, Any],
        related_threat_types: Optional[List[str]] = None,
        is_critical: bool = False,
    ) -> DeploymentSecurityConfig:
        """
        Add a security configuration to a deployment recommendation.
        
        Args:
            recommendation_id: ID of the deployment recommendation
            category: Category of the security configuration
            name: Name of the configuration
            description: Description of the configuration
            configuration_value: Configuration details as a dict
            related_threat_types: Threat types this configuration addresses
            is_critical: Whether this configuration is critical
            
        Returns:
            The created DeploymentSecurityConfig object
        """
        config_value_json = json.dumps(configuration_value)
        related_threats_str = ','.join(related_threat_types) if related_threat_types else None
        
        security_config = DeploymentSecurityConfig(
            recommendation_id=recommendation_id,
            category=category,
            name=name,
            description=description,
            configuration_value=config_value_json,
            related_threat_types=related_threats_str,
            is_critical=is_critical
        )
        
        self.session.add(security_config)
        await self.session.commit()
        await self.session.refresh(security_config)
        
        return security_config
    
    async def get_recommendations_for_user(
        self, 
        user_id: int,
        active_only: bool = True,
        expired: bool = False,
        limit: int = 10
    ) -> List[DeploymentRecommendation]:
        """
        Get deployment recommendations for a user.
        
        Args:
            user_id: ID of the user
            active_only: Only return active recommendations
            expired: Include expired recommendations
            limit: Maximum number of recommendations to return
            
        Returns:
            List of DeploymentRecommendation objects
        """
        query = select(DeploymentRecommendation).where(
            DeploymentRecommendation.user_id == user_id
        ).options(
            selectinload(DeploymentRecommendation.security_configurations)
        )
        
        if active_only:
            query = query.where(DeploymentRecommendation.is_active == True)
            
        if not expired:
            # Only include recommendations that are not expired or have no expiration
            now = datetime.utcnow()
            query = query.where(
                (DeploymentRecommendation.expires_at.is_(None)) | 
                (DeploymentRecommendation.expires_at > now)
            )
            
        query = query.order_by(DeploymentRecommendation.created_at.desc()).limit(limit)
        
        result = await self.session.execute(query)
        recommendations = result.scalars().all()
        
        return recommendations
    
    async def mark_recommendation_applied(
        self, 
        recommendation_id: int, 
        applied_at: Optional[datetime] = None
    ) -> DeploymentRecommendation:
        """
        Mark a deployment recommendation as applied.
        
        Args:
            recommendation_id: ID of the recommendation
            applied_at: When the recommendation was applied
            
        Returns:
            The updated DeploymentRecommendation object
        """
        if applied_at is None:
            applied_at = datetime.utcnow()
            
        query = update(DeploymentRecommendation).where(
            DeploymentRecommendation.id == recommendation_id
        ).values(
            is_applied=True,
            applied_at=applied_at
        ).returning(DeploymentRecommendation)
        
        result = await self.session.execute(query)
        recommendation = result.scalars().first()
        
        if recommendation:
            await self.session.commit()
            
        return recommendation
    
    async def record_deployment(
        self,
        user_id: int,
        title: str,
        description: Optional[str] = None,
        recommendation_id: Optional[int] = None,
        platform: Optional[DeploymentPlatform] = None,
        region: Optional[DeploymentRegion] = None,
        security_level: Optional[SecurityConfigLevel] = None,
        security_config_summary: Optional[str] = None,
        was_successful: bool = True,
        failure_reason: Optional[str] = None,
        actual_cost: Optional[float] = None,
        deployed_at: Optional[datetime] = None
    ) -> DeploymentHistory:
        """
        Record a deployment in the deployment history.
        
        Args:
            user_id: ID of the user who made the deployment
            title: Title of the deployment
            description: Description of the deployment
            recommendation_id: ID of the recommendation that was applied
            platform: Deployment platform
            region: Deployment region
            security_level: Security level applied
            security_config_summary: Summary of security configurations
            was_successful: Whether the deployment was successful
            failure_reason: Reason for failure if not successful
            actual_cost: Actual cost of the deployment
            deployed_at: When the deployment was made
            
        Returns:
            The created DeploymentHistory object
        """
        if deployed_at is None:
            deployed_at = datetime.utcnow()
            
        deployment = DeploymentHistory(
            user_id=user_id,
            title=title,
            description=description,
            recommendation_id=recommendation_id,
            platform=platform,
            region=region,
            security_level=security_level,
            security_config_summary=security_config_summary,
            was_successful=was_successful,
            failure_reason=failure_reason,
            actual_cost=actual_cost,
            deployed_at=deployed_at
        )
        
        self.session.add(deployment)
        await self.session.commit()
        await self.session.refresh(deployment)
        
        return deployment
    
    async def get_deployment_history(
        self, 
        user_id: int,
        limit: int = 10,
        successful_only: bool = False
    ) -> List[DeploymentHistory]:
        """
        Get deployment history for a user.
        
        Args:
            user_id: ID of the user
            limit: Maximum number of records to return
            successful_only: Only return successful deployments
            
        Returns:
            List of DeploymentHistory objects
        """
        query = select(DeploymentHistory).where(
            DeploymentHistory.user_id == user_id
        )
        
        if successful_only:
            query = query.where(DeploymentHistory.was_successful == True)
            
        query = query.order_by(DeploymentHistory.deployed_at.desc()).limit(limit)
        
        result = await self.session.execute(query)
        history = result.scalars().all()
        
        return history
    
    async def generate_threat_based_recommendations(
        self, 
        user_id: int,
        look_back_days: int = 7,
        threat_threshold: float = 0.5
    ) -> Optional[DeploymentRecommendation]:
        """
        Generate deployment recommendations based on current threat intelligence.
        
        Args:
            user_id: ID of the user
            look_back_days: Number of days to look back for threat data
            threat_threshold: Threshold for considering a threat significant
            
        Returns:
            A DeploymentRecommendation object if threats warrant a recommendation,
            None otherwise
        """
        # Get user subscription tier to determine recommendation capabilities
        subscription_query = select(UserSubscription).where(
            UserSubscription.user_id == user_id
        ).join(SubscriptionPlan).order_by(UserSubscription.created_at.desc()).limit(1)
        
        subscription_result = await self.session.execute(subscription_query)
        subscription = subscription_result.scalars().first()
        
        if not subscription:
            logger.warning(f"No subscription found for user {user_id}")
            # Default to FREE tier capabilities
            tier = SubscriptionTier.FREE
        else:
            tier = subscription.plan.tier
        
        # Get recent threats within the lookback period
        start_date = datetime.utcnow() - timedelta(days=look_back_days)
        
        threats_query = select(Threat).where(
            Threat.discovered_at >= start_date
        ).order_by(Threat.discovered_at.desc())
        
        threats_result = await self.session.execute(threats_query)
        threats = threats_result.scalars().all()
        
        if not threats:
            logger.info("No recent threats found for recommendation generation")
            return None
        
        # Count threats by severity
        critical_threats = [t for t in threats if t.severity == ThreatSeverity.CRITICAL]
        high_threats = [t for t in threats if t.severity == ThreatSeverity.HIGH]
        medium_threats = [t for t in threats if t.severity == ThreatSeverity.MEDIUM]
        low_threats = [t for t in threats if t.severity == ThreatSeverity.LOW]
        
        critical_count = len(critical_threats)
        high_count = len(high_threats)
        medium_count = len(medium_threats)
        low_count = len(low_threats)
        
        # Calculate a threat score based on severity weights
        severity_weights = {
            ThreatSeverity.CRITICAL: 1.0,
            ThreatSeverity.HIGH: 0.7,
            ThreatSeverity.MEDIUM: 0.4,
            ThreatSeverity.LOW: 0.1
        }
        
        threat_score = sum(severity_weights[t.severity] for t in threats) / len(threats)
        
        # Determine deployment timing recommendation based on threat score
        if threat_score > 0.7:
            timing = DeploymentTimingRecommendation.HIGH_RISK
            timing_justification = f"High concentration of critical and high severity threats detected in the past {look_back_days} days."
        elif threat_score > 0.4:
            timing = DeploymentTimingRecommendation.DELAY_RECOMMENDED
            timing_justification = f"Multiple high and medium severity threats detected in the past {look_back_days} days."
        elif threat_score > 0.2:
            timing = DeploymentTimingRecommendation.CAUTION
            timing_justification = f"Some medium severity threats detected in the past {look_back_days} days."
        else:
            timing = DeploymentTimingRecommendation.SAFE_TO_DEPLOY
            timing_justification = f"No significant threats detected in the past {look_back_days} days."
        
        # Generate security recommendations based on threat categories
        security_level = self._determine_security_level(threat_score, tier)
        
        # Create a threat assessment summary
        threat_assessment = self._generate_threat_assessment_summary(
            critical_count, high_count, medium_count, low_count, 
            critical_threats, high_threats, medium_threats, 
            threat_score, timing
        )
        
        # Generate security settings based on threats
        security_settings = self._generate_security_settings(
            threats, threat_score, tier
        )
        
        # Create the recommendation
        recommendation = await self.create_recommendation(
            user_id=user_id,
            title=f"Deployment recommendation based on {len(threats)} recent threats",
            description=f"Automatic recommendation generated based on threat analysis over the past {look_back_days} days.",
            security_level=security_level,
            timing_recommendation=timing,
            timing_justification=timing_justification,
            recommended_window_start=datetime.utcnow() + timedelta(days=1) if timing != DeploymentTimingRecommendation.SAFE_TO_DEPLOY else datetime.utcnow(),
            recommended_window_end=datetime.utcnow() + timedelta(days=7),
            threat_assessment_summary=threat_assessment,
            security_settings=security_settings,
            high_risk_threats_count=critical_count + high_count,
            medium_risk_threats_count=medium_count,
            low_risk_threats_count=low_count,
            expires_at=datetime.utcnow() + timedelta(days=7)  # Recommendations expire after 7 days
        )
        
        # Add security configurations based on threat categories
        threat_categories = set(t.category for t in threats)
        
        # Add network security configurations if relevant threats
        if (ThreatCategory.MALWARE in threat_categories or 
            ThreatCategory.PHISHING in threat_categories or 
            ThreatCategory.RANSOMWARE in threat_categories):
            
            await self.add_security_config(
                recommendation_id=recommendation.id,
                category=SecurityConfigCategory.NETWORK,
                name="Enhanced Network Security",
                description="Implement enhanced network security controls to mitigate malware and ransomware threats.",
                configuration_value={
                    "enable_ip_filtering": True,
                    "restrict_outbound_connections": True,
                    "implement_network_segmentation": True,
                    "enable_deep_packet_inspection": tier != SubscriptionTier.FREE
                },
                related_threat_types=["Malware", "Ransomware", "Phishing"],
                is_critical=ThreatCategory.RANSOMWARE in threat_categories
            )
        
        # Add authentication security if credential leaks or identity theft threats
        if (ThreatCategory.CREDENTIAL_LEAK in threat_categories or 
            ThreatCategory.IDENTITY_THEFT in threat_categories):
            
            await self.add_security_config(
                recommendation_id=recommendation.id,
                category=SecurityConfigCategory.AUTHENTICATION,
                name="Enhanced Authentication Controls",
                description="Implement stronger authentication controls to mitigate credential theft risks.",
                configuration_value={
                    "require_mfa": True,
                    "password_rotation": True,
                    "ip_based_login_restrictions": True,
                    "session_timeout": 30,  # minutes
                    "brute_force_protection": True
                },
                related_threat_types=["Credential Leak", "Identity Theft"],
                is_critical=True
            )
        
        # Add WAF if web vulnerabilities are detected
        if ThreatCategory.VULNERABILITY in threat_categories:
            await self.add_security_config(
                recommendation_id=recommendation.id,
                category=SecurityConfigCategory.WAF,
                name="Web Application Firewall",
                description="Deploy WAF to protect against common web vulnerabilities.",
                configuration_value={
                    "enable_waf": True,
                    "block_sql_injection": True,
                    "block_xss": True,
                    "block_csrf": True,
                    "rate_limiting": True,
                    "geo_blocking": tier != SubscriptionTier.FREE
                },
                related_threat_types=["Vulnerability"],
                is_critical=True
            )
        
        # Add DDoS protection if APT or significant threats
        if (ThreatCategory.APT in threat_categories or 
            critical_count > 0 or
            high_count > 3):
            
            await self.add_security_config(
                recommendation_id=recommendation.id,
                category=SecurityConfigCategory.DDOS_PROTECTION,
                name="DDoS Protection",
                description="Implement DDoS protection to ensure service availability.",
                configuration_value={
                    "enable_ddos_protection": True,
                    "traffic_threshold": 1000,
                    "auto_scaling": tier in [SubscriptionTier.PROFESSIONAL, SubscriptionTier.ENTERPRISE],
                    "traffic_analysis": True
                },
                related_threat_types=["Advanced Persistent Threat", "DDoS"],
                is_critical=ThreatCategory.APT in threat_categories
            )
        
        return recommendation
    
    async def generate_cost_optimization_recommendations(
        self, 
        user_id: int,
        usage_data: Optional[Dict[str, Any]] = None
    ) -> Optional[DeploymentRecommendation]:
        """
        Generate deployment recommendations based on cost optimization.
        
        Args:
            user_id: ID of the user
            usage_data: Dictionary of usage data for cost optimization
            
        Returns:
            A DeploymentRecommendation object with cost optimization recommendations,
            None if no optimization opportunities found
        """
        # In a real implementation, this would analyze actual usage data
        # For demo, we'll generate some simulated cost optimization opportunities
        
        # Get user subscription tier
        subscription_query = select(UserSubscription).where(
            UserSubscription.user_id == user_id
        ).join(SubscriptionPlan).order_by(UserSubscription.created_at.desc()).limit(1)
        
        subscription_result = await self.session.execute(subscription_query)
        subscription = subscription_result.scalars().first()
        
        if not subscription:
            # Default to FREE tier capabilities
            tier = SubscriptionTier.FREE
        else:
            tier = subscription.plan.tier
        
        # Higher tier subscriptions get more detailed cost optimization
        if tier in [SubscriptionTier.PROFESSIONAL, SubscriptionTier.ENTERPRISE]:
            cost_saving_potential = 32.5
            detailed_analysis = True
        elif tier == SubscriptionTier.BASIC:
            cost_saving_potential = 18.0
            detailed_analysis = False
        else:
            cost_saving_potential = 10.0
            detailed_analysis = False
        
        # Create the recommendation
        recommendation = await self.create_recommendation(
            user_id=user_id,
            title="Cost Optimization Recommendations",
            description="Recommendations for optimizing deployment costs based on usage patterns and threat analysis.",
            security_level=SecurityConfigLevel.STANDARD,
            timing_recommendation=DeploymentTimingRecommendation.SAFE_TO_DEPLOY,
            timing_justification="Cost optimization can be applied at any time.",
            estimated_cost=100.0 - cost_saving_potential,
            cost_saving_potential=cost_saving_potential,
            cost_justification=f"Based on usage pattern analysis, we identified potential savings of approximately ${cost_saving_potential:.2f} per month.",
            recommended_platform=DeploymentPlatform.AWS if tier != SubscriptionTier.FREE else DeploymentPlatform.HUGGING_FACE,
            recommended_region=DeploymentRegion.US_EAST,
            security_settings={
                "enable_cost_monitoring": True,
                "auto_scaling": tier != SubscriptionTier.FREE,
                "reserved_instances": tier in [SubscriptionTier.PROFESSIONAL, SubscriptionTier.ENTERPRISE],
                "spot_instances": tier in [SubscriptionTier.PROFESSIONAL, SubscriptionTier.ENTERPRISE],
            },
            expires_at=datetime.utcnow() + timedelta(days=30)  # Cost recommendations valid for 30 days
        )
        
        # Add cost optimization configurations
        await self.add_security_config(
            recommendation_id=recommendation.id,
            category=SecurityConfigCategory.MONITORING,
            name="Cost Monitoring",
            description="Implement cost monitoring and alerting to track expenses.",
            configuration_value={
                "enable_cost_alerts": True,
                "budget_threshold": 80,  # Alert at 80% of budget
                "daily_cost_reports": detailed_analysis,
                "resource_tagging": True
            },
            is_critical=False
        )
        
        if tier != SubscriptionTier.FREE:
            await self.add_security_config(
                recommendation_id=recommendation.id,
                category=SecurityConfigCategory.NETWORK,
                name="Network Cost Optimization",
                description="Optimize network configuration to reduce data transfer costs.",
                configuration_value={
                    "use_cdn": True,
                    "compress_responses": True,
                    "optimize_api_calls": True,
                    "regional_endpoint_routing": detailed_analysis
                },
                is_critical=False
            )
        
        if tier in [SubscriptionTier.PROFESSIONAL, SubscriptionTier.ENTERPRISE]:
            await self.add_security_config(
                recommendation_id=recommendation.id,
                category=SecurityConfigCategory.COMPLIANCE,
                name="Resource Scheduling",
                description="Implement scheduling for non-production resources to reduce costs.",
                configuration_value={
                    "dev_environment_scheduling": True,
                    "test_environment_scheduling": True,
                    "automatic_shutdown": True,
                    "weekend_scaling_down": True
                },
                is_critical=False
            )
        
        return recommendation
    
    def _determine_security_level(self, threat_score: float, tier: SubscriptionTier) -> SecurityConfigLevel:
        """Determine the appropriate security level based on threat score and subscription tier."""
        if threat_score > 0.7:
            return SecurityConfigLevel.STRICT
        elif threat_score > 0.4:
            return SecurityConfigLevel.ENHANCED
        else:
            return SecurityConfigLevel.STANDARD
    
    def _generate_threat_assessment_summary(
        self, 
        critical_count: int, 
        high_count: int, 
        medium_count: int, 
        low_count: int,
        critical_threats: List[Threat],
        high_threats: List[Threat],
        medium_threats: List[Threat],
        threat_score: float,
        timing: DeploymentTimingRecommendation
    ) -> str:
        """Generate a summary of the threat assessment."""
        total_count = critical_count + high_count + medium_count + low_count
        
        summary_parts = [
            f"Threat Assessment Summary (Score: {threat_score:.2f})",
            f"Based on analysis of {total_count} recent threats:",
            f"- {critical_count} Critical severity threats",
            f"- {high_count} High severity threats",
            f"- {medium_count} Medium severity threats",
            f"- {low_count} Low severity threats",
            ""
        ]
        
        if critical_count > 0:
            summary_parts.append("Critical threats detected:")
            for i, threat in enumerate(critical_threats[:3]):  # List up to 3 critical threats
                summary_parts.append(f"  - {threat.title} ({threat.category.value})")
            if len(critical_threats) > 3:
                summary_parts.append(f"  - Plus {len(critical_threats) - 3} more critical threats")
            summary_parts.append("")
        
        if high_count > 0:
            summary_parts.append("Notable high severity threats:")
            for i, threat in enumerate(high_threats[:2]):  # List up to 2 high threats
                summary_parts.append(f"  - {threat.title} ({threat.category.value})")
            if len(high_threats) > 2:
                summary_parts.append(f"  - Plus {len(high_threats) - 2} more high severity threats")
            summary_parts.append("")
        
        summary_parts.append(f"Deployment timing recommendation: {timing.value}")
        
        if timing == DeploymentTimingRecommendation.HIGH_RISK:
            summary_parts.append("Strongly recommend delaying deployment until threat level decreases.")
        elif timing == DeploymentTimingRecommendation.DELAY_RECOMMENDED:
            summary_parts.append("Consider delaying deployment or implementing enhanced security measures.")
        elif timing == DeploymentTimingRecommendation.CAUTION:
            summary_parts.append("Proceed with caution and implement recommended security measures.")
        else:
            summary_parts.append("Current threat environment is favorable for deployment.")
        
        return "\n".join(summary_parts)
    
    def _generate_security_settings(
        self, 
        threats: List[Threat], 
        threat_score: float,
        tier: SubscriptionTier
    ) -> Dict[str, Any]:
        """Generate security settings based on threats and subscription tier."""
        # This would be much more sophisticated in a real implementation
        settings = {
            "network_security": {
                "enable_firewall": True,
                "enable_ids_ips": tier != SubscriptionTier.FREE,
                "restrict_ports": True,
                "enable_ddos_protection": threat_score > 0.5 and tier != SubscriptionTier.FREE
            },
            "authentication": {
                "require_mfa": threat_score > 0.3,
                "session_timeout": 30 if threat_score > 0.5 else 60,
                "password_complexity": "high" if threat_score > 0.5 else "medium"
            },
            "encryption": {
                "encrypt_data_at_rest": True,
                "encrypt_data_in_transit": True,
                "key_rotation": tier != SubscriptionTier.FREE
            },
            "monitoring": {
                "enable_security_monitoring": True,
                "log_retention_days": 90 if tier in [SubscriptionTier.PROFESSIONAL, SubscriptionTier.ENTERPRISE] else 30,
                "enable_anomaly_detection": tier in [SubscriptionTier.PROFESSIONAL, SubscriptionTier.ENTERPRISE]
            }
        }
        
        # Add more specific settings based on threat categories
        threat_categories = set(t.category for t in threats)
        
        if ThreatCategory.RANSOMWARE in threat_categories:
            settings["backup"] = {
                "enable_automated_backups": True,
                "backup_frequency": "daily",
                "offsite_backups": tier != SubscriptionTier.FREE,
                "backup_encryption": True
            }
        
        if ThreatCategory.DATA_BREACH in threat_categories:
            settings["data_protection"] = {
                "data_loss_prevention": tier in [SubscriptionTier.PROFESSIONAL, SubscriptionTier.ENTERPRISE],
                "sensitive_data_discovery": tier in [SubscriptionTier.PROFESSIONAL, SubscriptionTier.ENTERPRISE],
                "data_access_logging": True
            }
            
        return settings