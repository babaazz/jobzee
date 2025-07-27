import logging
from typing import Dict, Any, List
import json
from kafka import KafkaProducer
from kafka.errors import KafkaError

logger = logging.getLogger(__name__)

class JobApplicationProcessor:
    """Workflow for processing job applications"""
    
    def __init__(self, kafka_brokers: List[str], applications_topic: str):
        self.kafka_brokers = kafka_brokers
        self.applications_topic = applications_topic
        self.producer = None
        
    def connect_kafka(self):
        """Connect to Kafka producer"""
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=self.kafka_brokers,
                value_serializer=lambda x: json.dumps(x).encode('utf-8'),
                key_serializer=lambda x: x.encode('utf-8') if x else None
            )
            logger.info("Connected to Kafka producer")
        except KafkaError as e:
            logger.error(f"Failed to connect to Kafka: {e}")
            raise
            
    def process_job_matches(self, job_matches: List[Dict[str, Any]], 
                          user_id: str, request_id: str) -> Dict[str, Any]:
        """Process job matches and prepare application recommendations"""
        try:
            applications = []
            
            for job in job_matches:
                application = self._create_application(job, user_id, request_id)
                applications.append(application)
                
            # Send applications to Kafka
            self._send_applications(applications)
            
            return {
                'request_id': request_id,
                'user_id': user_id,
                'applications_created': len(applications),
                'applications': applications
            }
            
        except Exception as e:
            logger.error(f"Error processing job matches: {e}")
            return {
                'request_id': request_id,
                'user_id': user_id,
                'applications_created': 0,
                'error': str(e)
            }
            
    def _create_application(self, job: Dict[str, Any], user_id: str, 
                          request_id: str) -> Dict[str, Any]:
        """Create a job application from a job match"""
        try:
            application = {
                'application_id': f"app_{request_id}_{job.get('id', 'unknown')}",
                'user_id': user_id,
                'job_id': job.get('id'),
                'job_title': job.get('title'),
                'company': job.get('company'),
                'location': job.get('location'),
                'match_score': job.get('match_score', 0.0),
                'status': 'recommended',
                'created_at': self._get_current_timestamp(),
                'job_details': {
                    'description': job.get('description'),
                    'requirements': job.get('requirements', []),
                    'skills': job.get('skills', []),
                    'experience_level': job.get('experience_level'),
                    'salary_range': job.get('salary_range'),
                    'job_type': job.get('job_type'),
                    'remote_friendly': job.get('remote_friendly', False)
                }
            }
            
            return application
            
        except Exception as e:
            logger.error(f"Error creating application: {e}")
            return {}
            
    def _send_applications(self, applications: List[Dict[str, Any]]):
        """Send applications to Kafka topic"""
        if not self.producer:
            self.connect_kafka()
            
        try:
            for application in applications:
                future = self.producer.send(
                    self.applications_topic,
                    key=application['application_id'],
                    value=application
                )
                
                # Wait for the send to complete
                record_metadata = future.get(timeout=10)
                logger.info(f"Sent application {application['application_id']} to topic {record_metadata.topic}")
                
        except KafkaError as e:
            logger.error(f"Error sending applications to Kafka: {e}")
            raise
            
    def _get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format"""
        from datetime import datetime
        return datetime.utcnow().isoformat()
        
    def generate_application_summary(self, applications: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate a summary of applications"""
        try:
            if not applications:
                return {
                    'total_applications': 0,
                    'average_match_score': 0.0,
                    'companies': [],
                    'locations': [],
                    'top_skills': []
                }
                
            # Calculate statistics
            total_applications = len(applications)
            match_scores = [app.get('match_score', 0.0) for app in applications]
            average_match_score = sum(match_scores) / len(match_scores) if match_scores else 0.0
            
            # Collect unique companies and locations
            companies = list(set(app.get('company', '') for app in applications if app.get('company')))
            locations = list(set(app.get('location', '') for app in applications if app.get('location')))
            
            # Collect top skills
            all_skills = []
            for app in applications:
                job_details = app.get('job_details', {})
                skills = job_details.get('skills', [])
                all_skills.extend(skills)
                
            # Count skill frequency
            skill_counts = {}
            for skill in all_skills:
                skill_counts[skill] = skill_counts.get(skill, 0) + 1
                
            # Get top 10 skills
            top_skills = sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            top_skills = [skill for skill, count in top_skills]
            
            return {
                'total_applications': total_applications,
                'average_match_score': round(average_match_score, 3),
                'companies': companies,
                'locations': locations,
                'top_skills': top_skills,
                'match_score_range': {
                    'min': min(match_scores) if match_scores else 0.0,
                    'max': max(match_scores) if match_scores else 0.0
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating application summary: {e}")
            return {}
            
    def filter_applications_by_criteria(self, applications: List[Dict[str, Any]], 
                                      criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Filter applications based on user criteria"""
        try:
            filtered_applications = []
            
            for application in applications:
                if self._application_matches_criteria(application, criteria):
                    filtered_applications.append(application)
                    
            return filtered_applications
            
        except Exception as e:
            logger.error(f"Error filtering applications: {e}")
            return applications
            
    def _application_matches_criteria(self, application: Dict[str, Any], 
                                    criteria: Dict[str, Any]) -> bool:
        """Check if an application matches the filtering criteria"""
        try:
            # Check minimum match score
            min_score = criteria.get('min_match_score', 0.0)
            if application.get('match_score', 0.0) < min_score:
                return False
                
            # Check company filter
            companies = criteria.get('companies', [])
            if companies and application.get('company') not in companies:
                return False
                
            # Check location filter
            locations = criteria.get('locations', [])
            if locations and application.get('location') not in locations:
                return False
                
            # Check job type filter
            job_types = criteria.get('job_types', [])
            if job_types:
                job_details = application.get('job_details', {})
                job_type = job_details.get('job_type', '')
                if job_type not in job_types:
                    return False
                    
            # Check remote work preference
            remote_only = criteria.get('remote_only', False)
            if remote_only:
                job_details = application.get('job_details', {})
                if not job_details.get('remote_friendly', False):
                    return False
                    
            return True
            
        except Exception as e:
            logger.error(f"Error checking application criteria: {e}")
            return True  # Default to including the application
            
    def close(self):
        """Close the Kafka producer"""
        if self.producer:
            self.producer.close()
            logger.info("Kafka producer closed") 