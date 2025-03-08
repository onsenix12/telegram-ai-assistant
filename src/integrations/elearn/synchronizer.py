# src/integrations/elearn/synchronizer.py content
from typing import Dict, Any, List, Optional
from src.integrations.elearn.client import ELearnClient
import json
import os
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ELearnSynchronizer:
    """Synchronize data with SMU E-Learn."""
    
    def __init__(self, data_dir: str = 'data', dummy_mode=False):
        self.data_dir = data_dir
        self.elearn_client = ELearnClient(dummy_mode=dummy_mode)
        
        # Ensure data directory exists
        os.makedirs(data_dir, exist_ok=True)
        
        # Initialize sync metadata file if not exists
        sync_file = os.path.join(data_dir, 'elearn_sync.json')
        if not os.path.exists(sync_file):
            with open(sync_file, 'w') as f:
                json.dump({
                    'last_sync': None,
                    'courses': {}
                }, f)
    
    def sync_all(self) -> Dict[str, Any]:
        """
        Synchronize all data from E-Learn.
        
        Returns:
            Dictionary with sync results
        """
        logger.info("Starting full E-Learn synchronization")
        
        # Get courses
        courses = self.elearn_client.get_courses()
        
        # Sync each course
        results = {
            'courses_synced': 0,
            'materials_synced': 0,
            'assignments_synced': 0,
            'schedule_synced': 0,
            'errors': []
        }
        
        for course in courses:
            try:
                course_code = course['code']
                logger.info(f"Syncing course: {course_code}")
                
                # Sync course data
                self._save_course(course)
                results['courses_synced'] += 1
                
                # Sync course materials
                materials = self.elearn_client.get_course_materials(course_code)
                self._save_course_materials(course_code, materials)
                results['materials_synced'] += len(materials)
                
                # Sync course assignments
                assignments = self.elearn_client.get_course_assignments(course_code)
                self._save_course_assignments(course_code, assignments)
                results['assignments_synced'] += len(assignments)
                
                # Sync course schedule
                schedule = self.elearn_client.get_course_schedule(course_code)
                self._save_course_schedule(course_code, schedule)
                results['schedule_synced'] += len(schedule)
                
                # Update sync metadata
                self._update_sync_metadata(course_code)
            except Exception as e:
                logger.error(f"Error syncing course {course['code']}: {str(e)}")
                results['errors'].append({
                    'course': course['code'],
                    'error': str(e)
                })
        
        # Update last sync time
        self._update_last_sync()
        
        logger.info(f"E-Learn synchronization completed with results: {results}")
        
        return results
    
    def sync_course(self, course_code: str) -> Dict[str, Any]:
        """
        Synchronize a specific course from E-Learn.
        
        Args:
            course_code: The course code (e.g., IS621)
            
        Returns:
            Dictionary with sync results
        """
        logger.info(f"Starting synchronization for course: {course_code}")
        
        results = {
            'course_synced': False,
            'materials_synced': 0,
            'assignments_synced': 0,
            'schedule_synced': 0,
            'errors': []
        }
        
        try:
            # Sync course data
            course = self.elearn_client.get_course(course_code)
            if course:
                self._save_course(course)
                results['course_synced'] = True
                
                # Sync course materials
                materials = self.elearn_client.get_course_materials(course_code)
                self._save_course_materials(course_code, materials)
                results['materials_synced'] = len(materials)
                
                # Sync course assignments
                assignments = self.elearn_client.get_course_assignments(course_code)
                self._save_course_assignments(course_code, assignments)
                results['assignments_synced'] = len(assignments)
                
                # Sync course schedule
                schedule = self.elearn_client.get_course_schedule(course_code)
                self._save_course_schedule(course_code, schedule)
                results['schedule_synced'] = len(schedule)
                
                # Update sync metadata
                self._update_sync_metadata(course_code)
            else:
                results['errors'].append({
                    'course': course_code,
                    'error': 'Course not found'
                })
        except Exception as e:
            logger.error(f"Error syncing course {course_code}: {str(e)}")
            results['errors'].append({
                'course': course_code,
                'error': str(e)
            })
        
        logger.info(f"Course synchronization completed with results: {results}")
        
        return results
    
    def get_sync_status(self) -> Dict[str, Any]:
        """
        Get synchronization status.
        
        Returns:
            Dictionary with sync status
        """
        sync_file = os.path.join(self.data_dir, 'elearn_sync.json')
        
        try:
            with open(sync_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {
                'last_sync': None,
                'courses': {}
            }
    
    def get_course(self, course_code: str) -> Optional[Dict[str, Any]]:
        """
        Get course from local data.
        
        Args:
            course_code: The course code (e.g., IS621)
            
        Returns:
            Course dictionary or None if not found
        """
        course_file = os.path.join(self.data_dir, f'course_{course_code}.json')
        
        if os.path.exists(course_file):
            try:
                with open(course_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return None
        else:
            return None
    
    def get_course_materials(self, course_code: str) -> List[Dict[str, Any]]:
        """
        Get course materials from local data.
        
        Args:
            course_code: The course code (e.g., IS621)
            
        Returns:
            List of material dictionaries
        """
        materials_file = os.path.join(self.data_dir, f'materials_{course_code}.json')
        
        if os.path.exists(materials_file):
            try:
                with open(materials_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return []
        else:
            return []
    
    def get_course_assignments(self, course_code: str) -> List[Dict[str, Any]]:
        """
        Get course assignments from local data.
        
        Args:
            course_code: The course code (e.g., IS621)
            
        Returns:
            List of assignment dictionaries
        """
        assignments_file = os.path.join(self.data_dir, f'assignments_{course_code}.json')
        
        if os.path.exists(assignments_file):
            try:
                with open(assignments_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return []
        else:
            return []
    
    def get_course_schedule(self, course_code: str) -> List[Dict[str, Any]]:
        """
        Get course schedule from local data.
        
        Args:
            course_code: The course code (e.g., IS621)
            
        Returns:
            List of schedule dictionaries
        """
        schedule_file = os.path.join(self.data_dir, f'schedule_{course_code}.json')
        
        if os.path.exists(schedule_file):
            try:
                with open(schedule_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return []
        else:
            return []
    
    def _save_course(self, course: Dict[str, Any]) -> None:
        """Save course data to file."""
        course_file = os.path.join(self.data_dir, f'course_{course["code"]}.json')
        
        with open(course_file, 'w') as f:
            json.dump(course, f, indent=2)
    
    def _save_course_materials(self, course_code: str, materials: List[Dict[str, Any]]) -> None:
        """Save course materials to file."""
        materials_file = os.path.join(self.data_dir, f'materials_{course_code}.json')
        
        with open(materials_file, 'w') as f:
            json.dump(materials, f, indent=2)
    
    def _save_course_assignments(self, course_code: str, assignments: List[Dict[str, Any]]) -> None:
        """Save course assignments to file."""
        assignments_file = os.path.join(self.data_dir, f'assignments_{course_code}.json')
        
        with open(assignments_file, 'w') as f:
            json.dump(assignments, f, indent=2)
    
    def _save_course_schedule(self, course_code: str, schedule: List[Dict[str, Any]]) -> None:
        """Save course schedule to file."""
        schedule_file = os.path.join(self.data_dir, f'schedule_{course_code}.json')
        
        with open(schedule_file, 'w') as f:
            json.dump(schedule, f, indent=2)
    
    def _update_sync_metadata(self, course_code: str) -> None:
        """Update sync metadata for a course."""
        sync_file = os.path.join(self.data_dir, 'elearn_sync.json')
        
        # Load existing metadata
        with open(sync_file, 'r') as f:
            metadata = json.load(f)
        
        # Update course sync time
        metadata['courses'][course_code] = {
            'last_sync': datetime.now().isoformat()
        }
        
        # Save metadata
        with open(sync_file, 'w') as f:
            json.dump(metadata, f, indent=2)
    
    def _update_last_sync(self) -> None:
        """Update last sync time."""
        sync_file = os.path.join(self.data_dir, 'elearn_sync.json')
        
        # Load existing metadata
        with open(sync_file, 'r') as f:
            metadata = json.load(f)
        
        # Update last sync time
        metadata['last_sync'] = datetime.now().isoformat()
        
        # Save metadata
        with open(sync_file, 'w') as f:
            json.dump(metadata, f, indent=2)