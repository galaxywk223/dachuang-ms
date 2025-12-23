import logging
import time
from apps.projects.models import Project, ProjectPushRecord

logger = logging.getLogger(__name__)

class ExternalPushService:
    @staticmethod
    def push_project_data(project_id, target_platform="PROVINCIAL_PLATFORM"):
        """
        Simulate pushing project data to an external platform.
        """
        try:
            project = Project.objects.get(id=project_id)
            
            # payload simulation
            payload = {
                "project_title": project.title,
                "leader": project.leader.real_name,
                "members": [m.real_name for m in project.members.all()],
                "amount": float(project.budget),
                "description": project.description
            }
            
            # Create record directly
            record = ProjectPushRecord.objects.create(
                project=project,
                target=target_platform,
                payload=payload,
                status=ProjectPushRecord.PushStatus.PENDING
            )
            
            # Simulate networking delay
            time.sleep(1)
            
            # Success simulation
            record.status = ProjectPushRecord.PushStatus.SUCCESS
            record.response_message = "Success (Mock)"
            record.save()
            
            return True, "推送成功"
            
        except Project.DoesNotExist:
            return False, "项目不存在"
        except Exception as e:
            logger.error(f"Push failed: {e}")
            return False, str(e)
